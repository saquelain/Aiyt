"""Stroop test: say the COLOUR of each word, not the word. Gets faster each word."""
import random

from .. import sound
from ..canvas import Video, bg, ease, rrect, text, W

COLORS = {
    "RED": (1, 0.2, 0.2), "BLUE": (0.25, 0.5, 1), "GREEN": (0.2, 0.85, 0.3), "YELLOW": (1, 0.9, 0.1),
    "PURPLE": (0.7, 0.3, 1),
}

TITLES = [
    "Say the COLOR, not the word 🧠",
    "Your brain will glitch at the end 🧠",
    "Only 1% can finish this brain test 😵",
    "How far can you get? 🧠 (say the color)",
]


def make(out, seed=1, **opts):
    rng = random.Random(seed)
    n = int(opts.get("words", 16))
    first, last = float(opts.get("first", 1.3)), float(opts.get("last", 0.55))
    fps = 30
    names = list(COLORS)
    words = []
    t = 1.6
    for i in range(n):
        w = rng.choice(names)
        c = rng.choice([x for x in names if x != w])
        gap = first + (last - first) * i / (n - 1)
        words.append((t, w, c))
        t += gap
    t_end = t
    dur = t_end + 2.4

    mix = sound.Mix(dur)
    mix.add(0, sound.beat(dur, bpm=120, seed=seed, vol=0.5))
    for wt, _, _ in words:
        mix.add(wt, sound.pop(0.35))
    mix.add(t_end, sound.win())
    wav = out[:-4] + ".wav"
    mix.write(wav)

    v = Video(out, wav, fps)
    ctx = v.ctx
    for fi in range(int(dur * fps)):
        t = fi / fps
        bg(ctx, (0.04, 0.04, 0.07))
        if t < 1.6:
            text(ctx, "Say the COLOR", W / 2, 820, 110, outline=10)
            text(ctx, "NOT the word", W / 2, 960, 100, col=(1, 0.3, 0.3), outline=10)
            text(ctx, "ready?", W / 2, 1120, 60, col=(0.7, 0.7, 0.8))
        elif t < t_end:
            i = max(k for k, (wt, _, _) in enumerate(words) if wt <= t)
            wt, w, c = words[i]
            text(ctx, "say the COLOR", W / 2, 260, 64, col=(0.8, 0.8, 0.85), outline=6)
            s = 0.7 + 0.3 * ease((t - wt) / 0.12)
            text(ctx, w, W / 2, 1010, 230 * s, col=COLORS[c], outline=12, outline_col=(0.02, 0.02, 0.02))
            frac = (i + 1) / n
            rrect(ctx, 140, 1440, W - 280, 30, 15)
            ctx.set_source_rgba(1, 1, 1, 0.15)
            ctx.fill()
            rrect(ctx, 140, 1440, max(30, (W - 280) * frac), 30, 15)
            ctx.set_source_rgb(0.4, 1, 0.5)
            ctx.fill()
            text(ctx, f"{i + 1}/{n}", W / 2, 1560, 64, outline=6)
        else:
            text(ctx, "How far did", W / 2, 840, 100, outline=10)
            text(ctx, "you get?", W / 2, 970, 100, outline=10)
            text(ctx, "comment your number", W / 2, 1120, 56, col=(1, 0.85, 0.3), outline=6)
        v.emit()
    v.close()
    return {
        "length_s": round(dur, 1),
        "params": {"words": n, "first": first, "last": last},
        "title": rng.choice(TITLES),
        "tags": ["stroop test", "brain test", "say the color", "brain games", "focus test", "challenge",
                 "brain teaser"],
        "hashtags": "#shorts #braintest #stroop #challenge #braingames",
    }
