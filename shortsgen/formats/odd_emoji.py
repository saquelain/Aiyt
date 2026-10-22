"""Find the odd emoji: three levels, each a bigger grid with a closer look-alike."""
import math
import random

from .. import sound
from ..canvas import Video, bg, emoji, ease, hsv, pop_scale, rrect, text, W

PAIRS = {
    "easy": [("🍎", "🍏"), ("🐶", "🐱"), ("💙", "💚"), ("⚽", "🏀"), ("🌞", "🌝"), ("🍩", "🍪"), ("🐸", "🐢")],
    "medium": [("🚗", "🚙"), ("🐻", "🐨"), ("🧡", "💛"), ("😺", "😸"), ("🍋", "🍌"), ("🐰", "🐭"), ("🌲", "🌳")],
    "hard": [("😀", "😃"), ("😃", "😄"), ("🕐", "🕑"), ("😐", "😑"), ("🍐", "🍏"), ("🙂", "😊"), ("😗", "😙")],
}
LEVELS = [("LEVEL 1", "easy", 5, 7), ("LEVEL 2", "medium", 6, 9), ("LEVEL 3", "hard", 7, 10)]

TITLES = [
    "Find the odd one out 👀 Level 3 is impossible",
    "Only 1% can find all 3 👀",
    "Can you find the different emoji? 🔍",
    "Find it in 5 seconds 👀 (99% fail level 3)",
]


def make(out, seed=1, **opts):
    rng = random.Random(seed)
    think = float(opts.get("think", 5))
    fps = 30
    hue = rng.random()
    rounds = []
    t = 0.3
    for name, diff, cols, rows in LEVELS:
        a, b = rng.choice(PAIRS[diff])
        if rng.random() < 0.5:
            a, b = b, a
        odd = (rng.randrange(cols), rng.randrange(1, rows))
        rounds.append({"name": name, "diff": diff, "a": a, "b": b, "cols": cols, "rows": rows,
                       "odd": odd, "start": t, "reveal": t + think, "end": t + think + 1.6})
        t += think + 1.6
    dur = t + 1.8

    mix = sound.Mix(dur)
    mix.add(0, sound.beat(dur, bpm=118, seed=seed, vol=0.5))
    for r in rounds:
        mix.add(r["start"], sound.whoosh(seed=seed))
        for k in range(int(think)):
            mix.add(r["start"] + k + 0.5, sound.tick())
        mix.add(r["reveal"], sound.ding())
    mix.add(rounds[-1]["end"], sound.win())
    wav = out[:-4] + ".wav"
    mix.write(wav)

    v = Video(out, wav, fps)
    ctx = v.ctx
    for fi in range(int(dur * fps)):
        t = fi / fps
        bg(ctx, hsv(hue, 0.5, 0.25), hsv(hue + 0.1, 0.6, 0.1))
        r = next((r for r in rounds if r["start"] <= t < r["end"]), None)
        if r is None:
            text(ctx, "How many did\nyou find?", W / 2, 760, 96, outline=10)
            text(ctx, "1, 2 or all 3?", W / 2, 1060, 70, col=(1, 0.85, 0.3), outline=8)
            v.emit()
            continue
        lt = t - r["start"]
        text(ctx, "Find the odd one out", W / 2, 200, 72, outline=10)
        text(ctx, f"{r['name']} · {r['diff'].upper()}", W / 2, 300, 56,
             col={"easy": (0.5, 1, 0.5), "medium": (1, 0.8, 0.3), "hard": (1, 0.4, 0.4)}[r["diff"]], outline=7)
        cols, rows = r["cols"], r["rows"]
        cell = min((W - 80) / cols, 1050 / rows)
        gx = (W - cell * cols) / 2
        gy = 390
        rrect(ctx, gx - 20, gy - 20, cell * cols + 40, cell * rows + 40, 36)
        ctx.set_source_rgba(1, 1, 1, 0.09)
        ctx.fill()
        s = pop_scale(lt, 0.3)
        for cx in range(cols):
            for cy in range(rows):
                ch = r["b"] if (cx, cy) == r["odd"] else r["a"]
                x = gx + (cx + 0.5) * cell
                y = gy + (cy + 0.5) * cell
                emoji(ctx, ch, x, y, cell * 0.78 * s)
        if t < r["reveal"]:
            left = r["reveal"] - t
            rrect(ctx, 140, 1500, W - 280, 36, 18)
            ctx.set_source_rgba(1, 1, 1, 0.15)
            ctx.fill()
            rrect(ctx, 140, 1500, max(36, (W - 280) * left / think), 36, 18)
            ctx.set_source_rgb(*((1, 0.3, 0.3) if left < 2 else (1, 0.85, 0.3)))
            ctx.fill()
            text(ctx, f"{int(left) + 1}", W / 2, 1640, 110, outline=10)
        else:
            k = ease((t - r["reveal"]) / 0.35)
            ox, oy = r["odd"]
            x, y = gx + (ox + 0.5) * cell, gy + (oy + 0.5) * cell
            ctx.new_path()
            ctx.arc(x, y, cell * (0.62 + 1.2 * (1 - k)), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.2, 0.2, k)
            ctx.set_line_width(10)
            ctx.stroke()
            text(ctx, "Found it?", W / 2, 1610, 90, col=(0.5, 1, 0.5), outline=10)
        v.emit()
    v.close()
    return {
        "length_s": round(dur, 1),
        "params": {"rounds": [{k: r[k] for k in ("diff", "a", "b", "cols", "rows", "odd")} for r in rounds],
                   "think": think},
        "title": rng.choice(TITLES),
        "tags": ["find the odd one out", "find the difference", "emoji quiz", "brain test", "puzzle",
                 "spot the difference", "eye test"],
        "hashtags": "#shorts #findtheoddoneout #emojichallenge #puzzle #eyetest",
    }
