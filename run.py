"""Command line for the Shorts loop.

  python run.py make   --format emoji_math --exp D1-1 [--seed 7] [--opt think=4]
  python run.py frames --exp D1-1                     # contact sheet PNG to eyeball before upload
  python run.py upload --exp D1-1 [--title "..."] [--publish-at 2026-10-23T15:00:00Z]
  python run.py stats                                 # snapshot views for everything uploaded
  python run.py report                                # latest numbers per video and per format
  python run.py plan   [--slots 6]                    # which formats to make next (bandit)
  python run.py retention                             # avg % watched per video (YouTube Analytics)
  python run.py channel                               # channel totals + every upload
"""
import argparse
import datetime as dt
import fcntl
import json
import math
import os
import subprocess
import sys

MANIFEST = "manifest.jsonl"
STATS_LOG = "stats.jsonl"
STRATEGY = "strategy.json"


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.isoformat(timespec="seconds").replace("+00:00", "Z")


def parse(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path) if line.strip()]


def save_manifest(rows):
    with open(MANIFEST, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def strategy():
    return json.load(open(STRATEGY)) if os.path.exists(STRATEGY) else {}


def cmd_make(a):
    from shortsgen import formats
    opts = dict(o.split("=", 1) for o in a.opt)
    os.makedirs("out", exist_ok=True)
    path = f"out/{a.exp}.mp4"
    meta = formats.get(a.format).make(path, seed=a.seed, **opts)
    row = {"exp": a.exp, "format": a.format, "seed": a.seed, "opts": opts, "file": path,
           "made_at": iso(now()), **meta}
    with open(MANIFEST + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)      # several makes may run in parallel
        rows = [r for r in load_jsonl(MANIFEST) if r["exp"] != a.exp] + [row]
        save_manifest(rows)
    print(json.dumps(row, ensure_ascii=False))


def cmd_frames(a):
    row = next(r for r in load_jsonl(MANIFEST) if r["exp"] == a.exp)
    os.makedirs("out/frames", exist_ok=True)
    png = f"out/frames/{a.exp}.png"
    n = a.n
    rate = n / row["length_s"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", row["file"],
                    "-vf", f"fps={rate:.4f},scale=360:-1,tile={n}x1", "-frames:v", "1", png], check=True)
    print(png)


def cmd_upload(a):
    from shortsgen import yt
    rows = load_jsonl(MANIFEST)
    row = next(r for r in rows if r["exp"] == a.exp)
    if row.get("video_id"):
        sys.exit(f"{a.exp} already uploaded as {row['video_id']}")
    title = a.title or row["title"]
    extra = f"{row['description_extra']}\n\n" if row.get("description_extra") else ""
    desc = a.description or f"{title}\n\n{extra}{row.get('hashtags', '#shorts')}"
    vid = yt.upload(row["file"], title, desc, ["shorts"] + row.get("tags", []), publish_at=a.publish_at)
    row.update(video_id=vid, title=title, publish_at=a.publish_at or iso(now()), uploaded_at=iso(now()))
    save_manifest(rows)
    print(vid, f"https://youtube.com/shorts/{vid}")


def cmd_stats(a):
    from shortsgen import yt
    rows = [r for r in load_jsonl(MANIFEST) if r.get("video_id")]
    if not rows:
        sys.exit("nothing uploaded yet")
    s = yt.stats([r["video_id"] for r in rows])
    t = now()
    with open(STATS_LOG, "a") as f:
        for r in rows:
            v = s.get(r["video_id"], {})
            age = (t - parse(r["publish_at"])).total_seconds() / 3600
            f.write(json.dumps({"t": iso(t), "exp": r["exp"], "video_id": r["video_id"], "age_h": round(age, 1),
                                "views": v.get("views"), "likes": v.get("likes"), "comments": v.get("comments"),
                                "privacy": v.get("privacy")}) + "\n")
    cmd_report(a)


def latest_stats():
    last = {}
    for s in load_jsonl(STATS_LOG):
        last[s["exp"]] = s
    return last


def cmd_report(a):
    rows = [r for r in load_jsonl(MANIFEST) if r.get("video_id")]
    last = latest_stats()
    t = now()
    print(f"{'exp':8} {'format':12} {'age_h':>6} {'views':>6} {'likes':>5} {'v/h':>6}  title")
    by_fmt = {}
    for r in sorted(rows, key=lambda r: r["publish_at"]):
        s = last.get(r["exp"], {})
        age = (t - parse(r["publish_at"])).total_seconds() / 3600
        views = s.get("views")
        vph = views / age if views is not None and age > 0 else None
        print(f"{r['exp']:8} {r['format']:12} {age:6.1f} {views if views is not None else '-':>6} "
              f"{s.get('likes', '-'):>5} {('%.1f' % vph) if vph is not None else '-':>6}  {r['title']}")
        if views is not None and age > 0:
            by_fmt.setdefault(r["format"], []).append((age, views))
    print("\nper format: n, total views, best, median views")
    for f, vs in sorted(by_fmt.items(), key=lambda kv: -sum(v for _, v in kv[1])):
        views = sorted(v for _, v in vs)
        print(f"  {f:12} n={len(vs):2} total={sum(views):6} best={views[-1]:6} median={views[len(views) // 2]:6}")


def cmd_plan(a):
    """UCB bandit over formats. Reward = log(1 + views) of videos at least min_age_h old."""
    from shortsgen import formats
    st = strategy()
    min_age = st.get("min_age_h", 24)
    active = [f for f in formats.FORMATS if f not in st.get("retired", [])]
    last = latest_stats()
    t = now()
    rewards = {f: [] for f in active}
    for r in load_jsonl(MANIFEST):
        s = last.get(r["exp"])
        if r.get("video_id") and s and r["format"] in rewards and s.get("views") is not None:
            if (t - parse(r["publish_at"])).total_seconds() / 3600 >= min_age:
                rewards[r["format"]].append(math.log1p(s["views"]))
    total = sum(len(v) for v in rewards.values()) + 1
    counts = {f: len(v) for f, v in rewards.items()}
    means = {f: (sum(v) / len(v) if v else None) for f, v in rewards.items()}
    pick = []
    for _ in range(a.slots):
        def ucb(f):
            if counts[f] == 0:
                return float("inf")
            return means[f] + st.get("explore", 1.5) * math.sqrt(math.log(total) / counts[f])
        best = max(active, key=ucb)
        pick.append(best)
        if means[best] is None:
            means[best] = 0.0
        counts[best] += 1
        total += 1
    for f in active:
        m = sum(rewards[f]) / len(rewards[f]) if rewards[f] else None
        print(f"  {f:12} judged={len(rewards[f]):2} mean_log_views={('%.2f' % m) if m is not None else '-'}")
    print("next:", " ".join(pick))


def cmd_retention(a):
    from shortsgen import yt
    rows = [r for r in load_jsonl(MANIFEST) if r.get("video_id")]
    try:
        ret = yt.retention([r["video_id"] for r in rows], "2026-10-01", now().date().isoformat())
    except Exception as e:      # API not enabled in the Cloud project, or no data yet
        sys.exit(f"analytics unavailable: {str(e)[:300]}")
    for r in rows:
        x = ret.get(r["video_id"])
        print(f"{r['exp']:8} {r['format']:12} len={r['length_s']:5}s  " +
              (f"views={x['views']:5} avg_watched={x['avg_s']:5}s ({x['avg_pct']:.0f}%)" if x else "no analytics yet"))


def cmd_channel(a):
    from shortsgen import yt
    ch, items = yt.channel_uploads(a.limit)
    print(ch["snippet"]["title"], ch["id"], json.dumps(ch["statistics"]))
    s = yt.stats([v for v, _ in items])
    for vid, title in items:
        v = s.get(vid, {})
        print(f"{vid}  {v.get('views', '?'):>7} views {v.get('likes', '?'):>4} likes  "
              f"{v.get('privacy', '?'):8} {(v.get('publishAt') or v.get('published') or '')[:16]}  {title}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--format", required=True)
    m.add_argument("--exp", required=True)
    m.add_argument("--seed", type=int, default=1)
    m.add_argument("--opt", action="append", default=[], help="format option key=value")
    f = sub.add_parser("frames")
    f.add_argument("--exp", required=True)
    f.add_argument("--n", type=int, default=6)
    u = sub.add_parser("upload")
    u.add_argument("--exp", required=True)
    u.add_argument("--title")
    u.add_argument("--description")
    u.add_argument("--publish-at")
    sub.add_parser("stats")
    sub.add_parser("report")
    p = sub.add_parser("plan")
    p.add_argument("--slots", type=int, default=strategy().get("slots_per_day", 6))
    sub.add_parser("retention")
    c = sub.add_parser("channel")
    c.add_argument("--limit", type=int, default=100)
    a = ap.parse_args()
    {"make": cmd_make, "frames": cmd_frames, "upload": cmd_upload, "stats": cmd_stats, "report": cmd_report,
     "plan": cmd_plan, "retention": cmd_retention, "channel": cmd_channel}[a.cmd](a)


if __name__ == "__main__":
    main()
