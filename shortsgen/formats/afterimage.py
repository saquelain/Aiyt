"""Afterimage illusion: stare at the dot on an inverted-colour picture, then the
picture turns black & white and the brain paints the real colours back in."""
import math
import random

from .. import sound
from ..canvas import Video, bg, circle, rrect, text, W

X0, Y0, SW, SH = 90, 420, 900, 1050       # picture area


def _rect(ctx, cf, col, x, y, w, h):
    ctx.new_path()
    ctx.rectangle(X0 + x * SW, Y0 + y * SH, w * SW, h * SH)
    ctx.set_source_rgb(*cf(col))
    ctx.fill()


def scene_india(ctx, cf):
    _rect(ctx, cf, (1.0, 0.6, 0.2), 0, 0, 1, 1 / 3)
    _rect(ctx, cf, (1, 1, 1), 0, 1 / 3, 1, 1 / 3)
    _rect(ctx, cf, (0.07, 0.53, 0.03), 0, 2 / 3, 1, 1 / 3)
    cx, cy, r = X0 + SW / 2, Y0 + SH / 2, SH / 7
    ctx.set_source_rgb(*cf((0, 0, 0.5)))
    ctx.set_line_width(8)
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.stroke()
    for k in range(24):
        a = k * 2 * math.pi / 24
        ctx.move_to(cx, cy)
        ctx.line_to(cx + r * math.cos(a), cy + r * math.sin(a))
    ctx.set_line_width(3)
    ctx.stroke()


def scene_france(ctx, cf):
    for i, col in enumerate([(0, 0.14, 0.58), (1, 1, 1), (0.93, 0.16, 0.22)]):
        _rect(ctx, cf, col, i / 3, 0, 1 / 3, 1)


def scene_japan(ctx, cf):
    _rect(ctx, cf, (1, 1, 1), 0, 0, 1, 1)
    circle(ctx, X0 + SW / 2, Y0 + SH / 2, SW * 0.3, cf((0.74, 0, 0.18)))


def scene_brazil(ctx, cf):
    _rect(ctx, cf, (0, 0.61, 0.23), 0, 0, 1, 1)
    cx, cy = X0 + SW / 2, Y0 + SH / 2
    ctx.new_path()
    ctx.move_to(cx, Y0 + 60)
    ctx.line_to(X0 + SW - 50, cy)
    ctx.line_to(cx, Y0 + SH - 60)
    ctx.line_to(X0 + 50, cy)
    ctx.close_path()
    ctx.set_source_rgb(*cf((1, 0.87, 0)))
    ctx.fill()
    circle(ctx, cx, cy, SW * 0.26, cf((0, 0.15, 0.46)))


def scene_landscape(ctx, cf):
    _rect(ctx, cf, (0.3, 0.65, 1.0), 0, 0, 1, 0.62)
    circle(ctx, X0 + SW * 0.75, Y0 + SH * 0.18, 95, cf((1, 0.85, 0.1)))
    for (x, y, r) in [(0.2, 0.75, 0.45), (0.8, 0.8, 0.5)]:
        circle(ctx, X0 + x * SW, Y0 + y * SH + 120, r * SW, cf((0.15, 0.7, 0.2)))
    _rect(ctx, cf, (0.15, 0.7, 0.2), 0, 0.82, 1, 0.18)
    # house
    _rect(ctx, cf, (0.95, 0.85, 0.6), 0.36, 0.5, 0.28, 0.22)
    ctx.new_path()
    ctx.move_to(X0 + 0.32 * SW, Y0 + 0.5 * SH)
    ctx.line_to(X0 + 0.5 * SW, Y0 + 0.36 * SH)
    ctx.line_to(X0 + 0.68 * SW, Y0 + 0.5 * SH)
    ctx.close_path()
    ctx.set_source_rgb(*cf((0.85, 0.1, 0.1)))
    ctx.fill()
    _rect(ctx, cf, (0.45, 0.25, 0.1), 0.46, 0.6, 0.08, 0.12)
    for i in range(7):
        circle(ctx, X0 + (0.08 + i * 0.14) * SW, Y0 + 0.9 * SH, 26,
               cf([(1, 0.2, 0.5), (1, 0.9, 0.1), (0.6, 0.2, 1)][i % 3]))


def scene_rainbow(ctx, cf):
    _rect(ctx, cf, (0.55, 0.85, 1), 0, 0, 1, 1)
    cols = [(0.9, 0.1, 0.1), (1, 0.5, 0), (1, 0.9, 0), (0.1, 0.75, 0.2), (0.1, 0.4, 1), (0.5, 0.1, 0.8)]
    cx, cy = X0 + SW / 2, Y0 + SH * 0.8
    for i, col in enumerate(cols):
        ctx.new_path()
        ctx.arc(cx, cy, SW * 0.48 - i * 55, math.pi, 2 * math.pi)
        ctx.set_line_width(55)
        ctx.set_source_rgb(*cf(col))
        ctx.stroke()
    _rect(ctx, cf, (0.2, 0.75, 0.25), 0, 0.8, 1, 0.2)


SCENES = {
    "india": (scene_india, "the Indian flag 🇮🇳"),
    "france": (scene_france, "the French flag 🇫🇷"),
    "japan": (scene_japan, "the Japanese flag 🇯🇵"),
    "brazil": (scene_brazil, "the Brazil flag 🇧🇷"),
    "landscape": (scene_landscape, "this picture"),
    "rainbow": (scene_rainbow, "a rainbow 🌈"),
}

TITLES = [
    "Stare at the dot for 15 seconds… 🤯",
    "This black & white picture will turn COLOR 🤯",
    "Your brain will see colors that aren't there 😳",
    "Optical illusion: keep looking at the red dot 👁️",
]


def invert(c):
    return tuple(1 - x for x in c)


def gray(c):
    y = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    return (y, y, y)


def make(out, seed=1, **opts):
    rng = random.Random(seed)
    name = opts.get("scene") or rng.choice(list(SCENES))
    draw, label = SCENES[name]
    stare = float(opts.get("stare", 15))
    fps = 30
    t_switch = 0.8 + stare
    t_real = t_switch + 6
    dur = t_real + 2.0

    mix = sound.Mix(dur)
    # soft drone with a slow pulse so the stare doesn't feel dead
    for k in range(int(dur / 2)):
        mix.add(k * 2, sound.tone(110 * (1.5 if k % 4 == 3 else 1), 2.4, 0.22, decay=0.8))
    for k in range(5):
        mix.add(t_switch - 5 + k, sound.tick(0.4))
    mix.add(t_switch, sound.whoosh(0.5, 0.35, seed))
    mix.add(t_switch + 0.1, sound.ding(784))
    mix.add(t_real, sound.win(0.3))
    wav = out[:-4] + ".wav"
    mix.write(wav)

    v = Video(out, wav, fps)
    ctx = v.ctx
    for fi in range(int(dur * fps)):
        t = fi / fps
        bg(ctx, (0.02, 0.02, 0.03))
        if t < t_switch:
            cf = invert
            text(ctx, "Stare at the RED DOT", W / 2, 200, 78, outline=8)
            text(ctx, "don't move your eyes", W / 2, 290, 50, col=(1, 0.8, 0.3), outline=5)
        elif t < t_real:
            cf = gray
            text(ctx, "Keep looking at the dot", W / 2, 200, 74, outline=8)
            text(ctx, "it's in COLOR now!", W / 2, 290, 56, col=(0.4, 1, 0.5), outline=5)
        else:
            cf = lambda c: c
            text(ctx, "Did it work?", W / 2, 200, 84, outline=8)
            text(ctx, "comment YES or NO", W / 2, 290, 52, col=(1, 0.8, 0.3), outline=5)
        rrect(ctx, X0 - 8, Y0 - 8, SW + 16, SH + 16, 16)
        ctx.set_source_rgb(0.2, 0.2, 0.25)
        ctx.fill()
        ctx.save()
        rrect(ctx, X0, Y0, SW, SH, 10)
        ctx.clip()
        draw(ctx, cf)
        ctx.restore()
        if t < t_real:
            circle(ctx, X0 + SW / 2, Y0 + SH / 2, 16, (0, 0, 0))
            circle(ctx, X0 + SW / 2, Y0 + SH / 2, 11, (1, 0.05, 0.05))
        if 0.8 <= t < t_switch:
            text(ctx, f"{int(t_switch - t) + 1}", W / 2, 1640, 110, outline=10)
        v.emit()
    v.close()
    return {
        "length_s": round(dur, 1),
        "params": {"scene": name, "stare": stare},
        "title": rng.choice(TITLES),
        "description_extra": f"Stare at the red dot and you'll see {label} in full color.",
        "tags": ["optical illusion", "illusion", "afterimage", "brain trick", "mind blowing", "eye test",
                 "illusions that will blow your mind"],
        "hashtags": "#shorts #opticalillusion #illusion #braintricks #mindblowing",
    }
