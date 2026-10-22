"""Marble race: coloured marbles roll down zig-zag ramps with bumpers.
Viewers pick a colour; first across the finish line wins."""
import math
import random

from .. import sound
from ..canvas import Video, bg, circle, rrect, text, W

MARBLES = [
    ("RED", (1, 0.22, 0.22)), ("BLUE", (0.25, 0.5, 1)), ("GREEN", (0.2, 0.85, 0.35)),
    ("YELLOW", (1, 0.88, 0.1)), ("PURPLE", (0.68, 0.3, 1)), ("ORANGE", (1, 0.55, 0.1)),
    ("PINK", (1, 0.45, 0.78)), ("WHITE", (0.95, 0.95, 0.95)),
]
R = 22
G = 1800.0
LEFT, RIGHT = 40, 1040
FINISH_Y = 1420
FLOOR_Y = 1560

TITLES = [
    "Pick a color 👇 Marble race",
    "Which marble wins? 🏁 Pick one now",
    "Choose your marble before it starts 🏁",
    "Marble race: comment your color 👇",
]


class Ball:
    def __init__(self, i, x, y):
        self.i, self.x, self.y = i, x, y
        self.vx = self.vy = 0.0
        self.finished = None


def course(rng, n_ramps=6, top=380, gap=170, drop=70, hole=150):
    """Zig-zag ramps; one bumper in each drop hole randomises who falls first."""
    segs, pegs = [], []
    segs += [(LEFT, -200, LEFT, FLOOR_Y), (RIGHT, -200, RIGHT, FLOOR_Y), (LEFT, FLOOR_Y, RIGHT, FLOOR_Y)]
    for k in range(n_ramps):
        y = top + k * gap
        if k % 2 == 0:
            segs.append((LEFT, y, RIGHT - hole, y + drop))
            hx = RIGHT - hole / 2
        else:
            segs.append((RIGHT, y, LEFT + hole, y + drop))
            hx = LEFT + hole / 2
        if k < n_ramps - 1:
            pegs.append((hx + rng.uniform(-12, 12), y + drop + 40, 10))
    return segs, pegs


def _closest(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ax + t * dx, ay + t * dy


def simulate(seed, n_balls=8, gate_t=1.0, max_t=40.0):
    rng = random.Random(seed)
    segs, pegs = course(rng)
    gate = (230, 250, 850, 250)
    walls = [(230, 60, 230, 250), (850, 60, 850, 250)]
    order = list(range(len(MARBLES)))
    rng.shuffle(order)
    order = order[:n_balls]
    balls = [Ball(order[j], 270 + j * (540 / max(1, n_balls - 1)), 200 - (j % 2) * 30) for j in range(n_balls)]
    for b in balls:
        b.vx = rng.uniform(-30, 30)
    fps, sub = 60, 6
    dt = 1 / fps / sub
    frames, events, finish = [], [], []
    t = 0.0
    last_snd = {}
    while t < max_t:
        for _ in range(sub):
            t += dt
            active = segs + walls + ([gate] if t < gate_t else [])
            for b in balls:
                b.vy += G * dt
                b.vx *= 1 - 0.25 * dt
                b.x += b.vx * dt
                b.y += b.vy * dt
                for (ax, ay, bx, by) in active:
                    cx, cy = _closest(b.x, b.y, ax, ay, bx, by)
                    _collide(b, cx, cy, R, 0.25, events, t, last_snd, "ramp")
                for (px, py, pr) in pegs:
                    _collide(b, px, py, R + pr, 0.75, events, t, last_snd, "peg")
                if b.finished is None and b.y > FINISH_Y:
                    b.finished = t
                    finish.append((t, b.i))
                    events.append((t, "finish", b.i))
            for a in range(len(balls)):
                for c in range(a + 1, len(balls)):
                    _pair(balls[a], balls[c])
        frames.append([(b.x, b.y, b.i) for b in balls])
        if finish and t > finish[0][0] + 3.0:
            break
    return {"segs": segs, "pegs": pegs, "gate": gate, "walls": walls, "gate_t": gate_t,
            "frames": frames, "events": events, "finish": finish, "fps": fps}


def _collide(b, cx, cy, rad, e, events, t, last_snd, kind):
    dx, dy = b.x - cx, b.y - cy
    d2 = dx * dx + dy * dy
    if d2 >= rad * rad or d2 == 0:
        return
    d = math.sqrt(d2)
    nx, ny = dx / d, dy / d
    b.x, b.y = cx + nx * rad, cy + ny * rad
    vn = b.vx * nx + b.vy * ny
    if vn < 0:
        b.vx -= (1 + e) * vn * nx
        b.vy -= (1 + e) * vn * ny
        if -vn > 260 and t - last_snd.get(b.i, -1) > 0.07:
            last_snd[b.i] = t
            events.append((t, kind, b.i))


def _pair(a, b):
    dx, dy = b.x - a.x, b.y - a.y
    d2 = dx * dx + dy * dy
    if d2 >= 4 * R * R or d2 == 0:
        return
    d = math.sqrt(d2)
    nx, ny = dx / d, dy / d
    push = (2 * R - d) / 2
    a.x -= nx * push
    a.y -= ny * push
    b.x += nx * push
    b.y += ny * push
    rv = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny
    if rv < 0:
        j = -(1 + 0.8) * rv / 2
        a.vx -= j * nx
        a.vy -= j * ny
        b.vx += j * nx
        b.vy += j * ny


def lead_changes(sim):
    """How many times the lowest (most advanced) marble changes; a proxy for drama."""
    changes, leader = 0, None
    for fr in sim["frames"][::6]:
        lead = max(fr, key=lambda p: p[1])[2]
        if lead != leader:
            changes += leader is not None
            leader = lead
    return changes


def stuck(sim, secs=2.5):
    """True if any marble that hasn't finished barely moved over any `secs` window."""
    fps = sim["fps"]
    fr = sim["frames"]
    step = int(secs * fps)
    for a in range(int(sim["gate_t"] * fps) + fps, len(fr) - step, fps):
        for (x0, y0, i), (x1, y1, _) in zip(fr[a], fr[a + step]):
            if y0 < FINISH_Y and math.hypot(x1 - x0, y1 - y0) < 25:
                return True
    return False


def pick_sim(seed, lo=14, hi=26, tries=40):
    best = None
    for s in range(seed * 1000, seed * 1000 + tries):
        sim = simulate(s)
        if not sim["finish"] or stuck(sim):
            continue
        win_t = sim["finish"][0][0]
        score = lead_changes(sim) - (0 if lo <= win_t <= hi else 100)
        if best is None or score > best[0]:
            best = (score, s, sim)
    return best[1], best[2]


def make(out, seed=1, **opts):
    rng = random.Random(seed)
    sim_seed, sim = pick_sim(seed)
    fps = sim["fps"]
    frames = sim["frames"]
    dur = len(frames) / fps
    win_t, winner = sim["finish"][0]

    mix = sound.Mix(dur + 0.5)
    mix.add(0, sound.beat(dur + 0.5, bpm=132, seed=seed, vol=0.45))
    for t, kind, i in sim["events"]:
        if kind == "peg":
            mix.add(t, sound.tone(sound.PENTA[i % 5] * 2, 0.25, 0.22, decay=12))
        elif kind == "ramp":
            mix.add(t, sound.tick(0.08))
    mix.add(win_t, sound.win(0.5))
    wav = out[:-4] + ".wav"
    mix.write(wav)

    v = Video(out, wav, fps)
    ctx = v.ctx
    trails = {}
    for fi, fr in enumerate(frames):
        t = fi / fps
        bg(ctx, (0.05, 0.06, 0.1), (0.02, 0.02, 0.05))
        # finish line (checkered)
        sq = 30
        for k in range(int((RIGHT - LEFT) / sq)):
            for row in range(2):
                ctx.rectangle(LEFT + k * sq, FINISH_Y - sq + row * sq, sq, sq)
                ctx.set_source_rgba(*((1, 1, 1) if (k + row) % 2 else (0.1, 0.1, 0.1)), 0.8)
                ctx.fill()
        ctx.set_line_cap(1)
        lines = sim["segs"] + sim["walls"] + ([sim["gate"]] if t < sim["gate_t"] else [])
        for (ax, ay, bx, by) in lines:
            ctx.new_path()
            ctx.move_to(ax, ay)
            ctx.line_to(bx, by)
            ctx.set_line_width(12)
            ctx.set_source_rgb(0.55, 0.6, 0.75)
            ctx.stroke()
        for (px, py, pr) in sim["pegs"]:
            circle(ctx, px, py, pr + 3, (0.3, 0.32, 0.4))
            circle(ctx, px, py, pr, (0.75, 0.78, 0.9))
        for (x, y, i) in fr:
            tr = trails.setdefault(i, [])
            tr.append((x, y))
            del tr[:-8]
            col = MARBLES[i][1]
            for j, (tx, ty) in enumerate(tr[:-1]):
                circle(ctx, tx, ty, R * (0.3 + 0.5 * j / 8), col, 0.15)
        for (x, y, i) in fr:
            col = MARBLES[i][1]
            circle(ctx, x, y, R + 3, (0, 0, 0))
            circle(ctx, x, y, R, col)
            circle(ctx, x - 7, y - 7, 6, (1, 1, 1), 0.6)
        # header
        if t < win_t:
            lead = max(fr, key=lambda p: p[1])[2]
            text(ctx, "PICK YOUR COLOR", W / 2, 110, 70, outline=8)
            if t > sim["gate_t"] + 1:
                text(ctx, f"leading: {MARBLES[lead][0]}", W / 2, 190, 52, col=MARBLES[lead][1], outline=6)
        else:
            k = min(1, (t - win_t) / 0.25)
            rrect(ctx, 120, 40, W - 240, 200, 40)
            ctx.set_source_rgba(0, 0, 0, 0.75)
            ctx.fill()
            text(ctx, f"{MARBLES[winner][0]} WINS!", W / 2, 165, 100 * (0.7 + 0.3 * k),
                 col=MARBLES[winner][1], outline=10)
        v.emit()
    v.close()
    names = [MARBLES[i][0] for _, i in sim["finish"]]
    return {
        "length_s": round(dur, 1),
        "params": {"sim_seed": sim_seed, "winner": MARBLES[winner][0], "order": names,
                   "win_t": round(win_t, 1), "lead_changes": lead_changes(sim)},
        "title": rng.choice(TITLES),
        "tags": ["marble race", "marble run", "pick a color", "satisfying", "race", "physics simulation",
                 "oddly satisfying"],
        "hashtags": "#shorts #marblerace #satisfying #pickacolor #race",
    }
