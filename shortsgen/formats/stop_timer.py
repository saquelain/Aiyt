"""Pause-at-exactly challenge: a fast stopwatch; the target value is on screen
for exactly one frame. Ends where it starts so it loops."""
import math
import random

from .. import sound
from ..canvas import Video, bg, hsv, rrect, text, W, H

TITLES = [
    "Pause at exactly {target} ⏱️ (I bet you can't)",
    "Stop the timer at {target} 😤",
    "Only 1 in 1000 can stop at {target} ⏱️",
    "Try to pause at {target} 👀",
]


def make(out, seed=1, **opts):
    rng = random.Random(seed)
    fps = 30
    speed = float(opts.get("speed", 1.35))      # timer seconds per real second
    run = float(opts.get("run", 8.0))           # real seconds of counting
    end_value = run * speed
    # target must land on a displayed frame value
    frame_vals = [round(fi / fps * speed, 2) for fi in range(int(run * fps))]
    candidates = [v for v in frame_vals if 0.55 * end_value < v < 0.95 * end_value]
    target = rng.choice(candidates)
    hue = rng.random()
    dur = run + 1.2

    mix = sound.Mix(dur)
    mix.add(0, sound.beat(dur, bpm=128, seed=seed, vol=0.55))
    for k in range(int(run * 4)):
        mix.add(k * 0.25, sound.tick(0.18))
    mix.add(run, sound.buzz())
    wav = out[:-4] + ".wav"
    mix.write(wav)

    v = Video(out, wav, fps)
    ctx = v.ctx
    acc = hsv(hue, 0.85, 1.0)
    for fi in range(int(dur * fps)):
        t = fi / fps
        val = min(end_value, round(t * speed, 2)) if t < run else end_value
        bg(ctx, (0.03, 0.03, 0.06))
        text(ctx, "PAUSE AT EXACTLY", W / 2, 330, 76, outline=8)
        text(ctx, f"{target:.2f}", W / 2, 520, 190, col=acc, outline=12)
        # stopwatch face
        cx, cy, R = W / 2, 1030, 330
        ctx.new_path()
        ctx.arc(cx, cy, R, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.06)
        ctx.fill()
        frac = (val % 1.0)
        ctx.new_path()
        ctx.set_line_width(26)
        ctx.set_source_rgba(*acc, 0.9)
        ctx.arc(cx, cy, R - 20, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac)
        ctx.stroke()
        hit = abs(val - target) < 1e-6
        col = (0.3, 1, 0.4) if hit else (1, 1, 1)
        text(ctx, f"{val:05.2f}", cx, cy + 60, 165, col=col, outline=10, font="DejaVu Sans Mono")
        if t >= run:
            rrect(ctx, 90, 1440, W - 180, 170, 40)
            ctx.set_source_rgba(1, 0.25, 0.3, 0.9)
            ctx.fill()
            text(ctx, "Missed it? Try again", W / 2, 1550, 70, outline=6)
        else:
            text(ctx, "screenshot it or it didn't happen", W / 2, 1520, 44, col=(0.75, 0.75, 0.8), outline=4)
        v.emit()
    v.close()
    return {
        "length_s": round(dur, 1),
        "params": {"target": target, "speed": speed, "run": run},
        "title": rng.choice(TITLES).format(target=f"{target:.2f}"),
        "tags": ["stop the timer", "stopwatch challenge", "reaction test", "pause challenge", "try not to",
                 "challenge", "reflex test"],
        "hashtags": "#shorts #challenge #stopwatch #reactiontest #pausechallenge",
    }
