"""Shared drawing helpers: a 1080x1920 cairo canvas piped into ffmpeg."""
import functools
import math
import subprocess

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT = "DejaVu Sans"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


class Video:
    """Write cairo frames to an MP4 with the given WAV as soundtrack."""

    def __init__(self, path, wav, fps=30):
        self.fps = fps
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.ctx = cairo.Context(self.surf)
        self.n = 0
        self.ff = subprocess.Popen([
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
            "-i", wav,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", path,
        ], stdin=subprocess.PIPE)

    def emit(self):
        self.surf.flush()
        self.ff.stdin.write(self.surf.get_data())
        self.n += 1

    def close(self):
        self.ff.stdin.close()
        if self.ff.wait() != 0:
            raise RuntimeError("ffmpeg failed")


def bg(ctx, top, bottom=None):
    if bottom is None:
        ctx.set_source_rgb(*top)
    else:
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, *top)
        g.add_color_stop_rgb(1, *bottom)
        ctx.set_source(g)
    ctx.paint()


def text(ctx, s, cx, y, size, col=(1, 1, 1), outline=0.0, outline_col=(0, 0, 0), bold=True,
         max_w=W - 80, font=FONT, align="center"):
    """Draw text centred on cx with baseline y; shrinks to fit max_w. Multi-line with \\n."""
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    lines = s.split("\n")
    ctx.set_font_size(size)
    widest = max(ctx.text_extents(line).x_advance for line in lines)
    if widest > max_w:
        size *= max_w / widest
        ctx.set_font_size(size)
    for li, line in enumerate(lines):
        ext = ctx.text_extents(line)
        x = cx - ext.x_advance / 2 if align == "center" else cx
        yy = y + li * size * 1.18
        ctx.new_path()
        ctx.move_to(x, yy)
        ctx.text_path(line)
        if outline:
            ctx.set_source_rgb(*outline_col)
            ctx.set_line_width(outline)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke_preserve()
        ctx.set_source_rgb(*col)
        ctx.fill()
    return size


def rrect(ctx, x, y, w, h, r):
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def circle(ctx, x, y, r, col, alpha=1.0):
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgba(*col, alpha)
    ctx.fill()


def hsv(h, s, v):
    h = h % 1
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    return [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]


def pil_to_surface(img):
    """RGBA PIL image -> premultiplied cairo surface."""
    a = np.asarray(img.convert("RGBA"), dtype=np.float32)
    alpha = a[..., 3:4] / 255
    bgra = np.empty_like(a)
    bgra[..., 0] = a[..., 2] * alpha[..., 0]
    bgra[..., 1] = a[..., 1] * alpha[..., 0]
    bgra[..., 2] = a[..., 0] * alpha[..., 0]
    bgra[..., 3] = a[..., 3]
    data = bytearray(np.ascontiguousarray(bgra.astype(np.uint8)).tobytes())
    h, w = a.shape[:2]
    return cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, w, h, w * 4)


@functools.lru_cache(maxsize=256)
def emoji_surface(ch):
    """A colour emoji rendered at the font's native 109px size."""
    font = ImageFont.truetype(EMOJI_FONT, 109)
    img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((8, 8), ch, font=font, embedded_color=True)
    return pil_to_surface(img.crop(img.getbbox()))


def emoji(ctx, ch, cx, cy, size, alpha=1.0, angle=0.0):
    """Draw an emoji centred at (cx, cy), `size` px tall."""
    if size < 1:
        return
    s = emoji_surface(ch)
    k = size / s.get_height()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(angle)
    ctx.scale(k, k)
    ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def pop_scale(t, dur=0.25):
    """Overshoot scale for a pop-in starting at t=0."""
    if t <= 0:
        return 0.0
    if t >= dur:
        return 1.0
    x = t / dur
    return 1 + 0.25 * math.sin(math.pi * x) - (1 - x) ** 2 * 1.0
