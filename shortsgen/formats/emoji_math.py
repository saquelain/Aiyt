"""Emoji equation puzzle: three clue lines, one question, countdown, answer.

The question mixes + and × so order-of-operations splits the comments.
"""
import random

from .. import sound
from ..canvas import Video, bg, emoji, ease, hsv, pop_scale, rrect, text, W

SETS = [
    ("🍎", "🍌", "🍒"), ("🍔", "🍟", "🥤"), ("🐶", "🐱", "🐭"), ("⚽", "🏀", "🎾"),
    ("🍕", "🍩", "🍪"), ("🚗", "🚲", "🛵"), ("🌟", "🌙", "☀️"), ("🍓", "🍇", "🍋"),
    ("🦁", "🐯", "🐵"), ("🎸", "🥁", "🎺"), ("💎", "👑", "💰"), ("🍦", "🧁", "🍫"),
]

TITLES = {
    "en": ["Only 1% can solve this emoji puzzle 🧠", "Can you solve this in 5 seconds? 🤯",
           "Most people get this WRONG 😳", "Your IQ if you solve this 👀", "99% fail this emoji math 🧠"],
    "hi": ["Sirf 1% log solve kar paate hain 🧠", "99% log galat answer dete hain 😳",
           "5 second mein solve karo 🤯 (no calculator)"],
}
STR = {
    "en": {"head": "Only 1% can solve this", "sub": "no calculator!", "end": "Did you get it right?",
           "end2": "comment your answer"},
    "hi": {"head": "Sirf 1% solve kar paate hain", "sub": "calculator mat use karna!", "end": "Sahi answer mila?",
           "end2": "comment mein answer likho"},
}


def puzzle(rng):
    a, b, c = rng.randint(3, 10), rng.randint(2, 6), rng.randint(1, 5)
    while len({a, b, c}) < 3:
        c = rng.randint(1, 5)
    lines = [
        ([0, 0, 0], "+", 3 * a),
        ([0, 1, 1], "+", a + 2 * b),
        ([1, 2, 2], "+", b + 2 * c),
    ]
    q = rng.choice(["c+a*b", "a+b*c", "c*a+b"])
    vals = {"a": a, "b": b, "c": c}
    ans = eval(q, {}, vals)
    qidx = [{"a": 0, "b": 1, "c": 2}[ch] for ch in q[::2]]
    qops = [q[1], q[3]]
    return (a, b, c), lines, qidx, qops, ans


def make(out, seed=1, **opts):
    rng = random.Random(seed)
    icons = rng.choice(SETS)
    (a, b, c), lines, qidx, qops, ans = puzzle(rng)
    hue = rng.random()
    fps = 30
    t_lines = [0.6, 1.5, 2.4]
    t_q = 3.4
    think = float(opts.get("think", 5))
    lang = opts.get("lang", "en")
    S = STR[lang]
    t_ans = t_q + 0.6 + think
    dur = t_ans + 3.2

    mix = sound.Mix(dur)
    mix.add(0, sound.beat(dur, bpm=100, seed=seed, vol=0.6))
    for t in t_lines:
        mix.add(t, sound.pop())
    mix.add(t_q, sound.whoosh(seed=seed))
    for k in range(int(think)):
        mix.add(t_q + 0.6 + k, sound.tick())
    mix.add(t_ans, sound.win())
    wav = out[:-4] + ".wav"
    mix.write(wav)

    v = Video(out, wav, fps)
    ctx = v.ctx
    sym = {"*": "×", "+": "+"}
    nframes = int(dur * fps)
    for fi in range(nframes):
        t = fi / fps
        bg(ctx, hsv(hue, 0.6, 0.22), hsv(hue + 0.12, 0.7, 0.12))
        text(ctx, S["head"], W / 2, 230, 74, outline=10)
        text(ctx, S["sub"], W / 2, 320, 46, col=(1, 0.85, 0.3), outline=6)
        y0 = 500
        for li, (idx, op, val) in enumerate(lines):
            s = pop_scale(t - t_lines[li])
            if s <= 0:
                continue
            y = y0 + li * 230
            ctx.save()
            ctx.translate(W / 2, y)
            ctx.scale(s, s)
            ctx.translate(-W / 2, -y)
            rrect(ctx, 60, y - 100, W - 120, 190, 40)
            ctx.set_source_rgba(1, 1, 1, 0.08)
            ctx.fill()
            xs = [135, 335, 535]
            for j, ic in enumerate(idx):
                emoji(ctx, icons[ic], xs[j], y - 5, 115)
                if j < 2:
                    text(ctx, op, xs[j] + 100, y + 25, 70)
            text(ctx, f"= {val}", 835, y + 30, 96, outline=8)
            ctx.restore()
        # question line
        s = pop_scale(t - t_q)
        if s > 0:
            y = y0 + 3 * 230 + 40
            ctx.save()
            ctx.translate(W / 2, y)
            ctx.scale(s, s)
            ctx.translate(-W / 2, -y)
            rrect(ctx, 50, y - 115, W - 100, 220, 46)
            ctx.set_source_rgba(*hsv(hue + 0.5, 0.8, 0.9), 0.35)
            ctx.fill()
            xs = [135, 335, 535]
            for j, ic in enumerate(qidx):
                emoji(ctx, icons[ic], xs[j], y - 5, 120)
                if j < 2:
                    text(ctx, sym[qops[j]], xs[j] + 100, y + 25, 74)
            if t < t_ans:
                text(ctx, "= ?", 835, y + 35, 110, col=(1, 0.9, 0.3), outline=8)
            else:
                k = ease((t - t_ans) / 0.3)
                text(ctx, f"= {ans}", 835, y + 35, 110 * (0.6 + 0.4 * k), col=(0.4, 1, 0.5), outline=8)
            ctx.restore()
        # countdown bar
        if t_q + 0.6 <= t < t_ans:
            left = t_ans - t
            frac = left / think
            rrect(ctx, 140, 1385, W - 280, 40, 20)
            ctx.set_source_rgba(1, 1, 1, 0.15)
            ctx.fill()
            rrect(ctx, 140, 1385, max(40, (W - 280) * frac), 40, 20)
            ctx.set_source_rgb(*((1, 0.3, 0.3) if left < 2 else (1, 0.85, 0.3)))
            ctx.fill()
            text(ctx, f"{int(left) + 1}", W / 2, 1505, 120, outline=10)
        elif t >= t_ans:
            text(ctx, S["end"], W / 2, 1440, 70, outline=8)
            text(ctx, S["end2"], W / 2, 1515, 50, col=(0.85, 0.85, 0.9), outline=5)
        v.emit()
    v.close()
    return {
        "length_s": round(dur, 1),
        "params": {"icons": icons, "values": [a, b, c], "question": qops, "answer": ans, "think": think, "lang": lang},
        "title": rng.choice(TITLES[lang]),
        "lang": lang,
        "tags": ["emoji puzzle", "math puzzle", "brain teaser", "iq test", "riddles", "quiz", "puzzle"],
        "hashtags": "#shorts #puzzle #brainteaser #math #iqtest",
    }
