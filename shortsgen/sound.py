"""Synthesized sound effects and background beats, mixed into one WAV."""
import wave

import numpy as np

SR = 44100
PENTA = [261.63, 293.66, 329.63, 392.00, 440.00]


def _t(dur):
    return np.arange(int(SR * dur)) / SR


def tone(freq, dur=0.3, vol=0.4, decay=8, harmonics=(1, 0.3, 0.1)):
    t = _t(dur)
    w = sum(a * np.sin(2 * np.pi * freq * (i + 1) * t) for i, a in enumerate(harmonics))
    return vol * w * np.exp(-t * decay) * np.minimum(1, t * 400)


def tick(vol=0.35):
    t = _t(0.05)
    return vol * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120)


def pop(vol=0.4):
    t = _t(0.12)
    f = 900 * np.exp(-t * 25) + 200
    return vol * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)


def ding(freq=1046.5, vol=0.45):
    return tone(freq, 1.2, vol, decay=3.5, harmonics=(1, 0.5, 0.25, 0.12))


def win(vol=0.4):
    out = np.zeros(int(SR * 1.4))
    for j, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        c = tone(f, 1.0, vol, decay=4, harmonics=(1, 0.4, 0.2))
        i = int(j * 0.09 * SR)
        out[i:i + len(c)] += c[: len(out) - i]
    return out


def buzz(vol=0.3):
    t = _t(0.35)
    return vol * np.sign(np.sin(2 * np.pi * 110 * t)) * np.exp(-t * 6)


def whoosh(dur=0.4, vol=0.25, seed=0):
    t = _t(dur)
    n = np.random.default_rng(seed).normal(0, 1, len(t))
    env = np.sin(np.pi * t / dur) ** 2
    # crude band-limit: moving average
    k = 12
    n = np.convolve(n, np.ones(k) / k, mode="same")
    return vol * n * env * 3


def kick(vol=0.6):
    t = _t(0.25)
    f = 120 * np.exp(-t * 30) + 45
    return vol * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)


def hat(vol=0.12, seed=0):
    t = _t(0.05)
    return vol * np.random.default_rng(seed).normal(0, 1, len(t)) * np.exp(-t * 90)


def beat(duration, bpm=110, seed=0, root=None, vol=1.0):
    """A simple loopable lo-fi beat: kick, hats and a pentatonic bass line."""
    rng = np.random.default_rng(seed)
    root = root or float(rng.choice([55.0, 61.74, 65.41, 73.42]))
    step = 60 / bpm / 2          # eighth notes
    out = np.zeros(int(SR * (duration + 1)))
    bass_pat = rng.choice([0, 0, 2, 3, 4], size=8)
    n = int(duration / step)
    for i in range(n):
        t0 = i * step
        if i % 4 == 0:
            _add(out, t0, kick(0.5 * vol))
        _add(out, t0, hat(0.06 * vol, seed=i))
        if i % 2 == 0:
            f = root * PENTA[bass_pat[(i // 2) % 8]] / PENTA[0]
            _add(out, t0, tone(f, step * 1.8, 0.22 * vol, decay=5, harmonics=(1, 0.5, 0.2)))
    return out[: int(SR * duration)]


def _add(buf, start, clip):
    i = int(start * SR)
    if i >= len(buf) or i + len(clip) <= 0:
        return
    j = min(len(buf), i + len(clip))
    buf[max(0, i):j] += clip[max(0, -i): j - i]


class Mix:
    def __init__(self, duration):
        self.buf = np.zeros(int(SR * duration))

    def add(self, t, clip):
        _add(self.buf, t, clip)

    def write(self, path):
        b = self.buf
        peak = np.max(np.abs(b)) or 1
        b = np.tanh(b / peak * 1.4) * 0.85
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((b * 32767).astype(np.int16).tobytes())
