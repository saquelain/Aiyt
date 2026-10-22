"""Command line for the Shorts loop.

  python run.py channel                 # channel totals + every upload with views
  python run.py stats                   # snapshot stats for everything in manifest.jsonl
"""
import argparse
import datetime as dt
import json
import os
import sys

MANIFEST = "manifest.jsonl"
STATS_LOG = "stats.jsonl"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_manifest():
    if not os.path.exists(MANIFEST):
        return []
    return [json.loads(line) for line in open(MANIFEST) if line.strip()]


def save_manifest(rows):
    with open(MANIFEST, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def cmd_channel(a):
    from shortsgen import yt
    ch, items = yt.channel_uploads(a.limit)
    print(ch["snippet"]["title"], ch["id"], json.dumps(ch["statistics"]))
    s = yt.stats([v for v, _ in items])
    for vid, title in items:
        v = s.get(vid, {})
        print(f"{vid}  {v.get('views', '?'):>7} views {v.get('likes', '?'):>4} likes  "
              f"{v.get('privacy', '?'):8} {(v.get('publishAt') or v.get('published') or '')[:16]}  {title}")


def cmd_stats(a):
    from shortsgen import yt
    rows = [r for r in load_manifest() if r.get("video_id")]
    if not rows:
        sys.exit("nothing uploaded yet")
    s = yt.stats([r["video_id"] for r in rows])
    t = now()
    with open(STATS_LOG, "a") as f:
        for r in rows:
            v = s.get(r["video_id"], {})
            f.write(json.dumps({"t": t, "exp": r["exp"], "video_id": r["video_id"], **v}, ensure_ascii=False) + "\n")
            print(f"{r['exp']:6} {r.get('format', ''):14} {v.get('views', '?'):>7} views "
                  f"{v.get('likes', '?'):>4} likes  {v.get('privacy', '?'):8} {v.get('title', '')}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("channel")
    c.add_argument("--limit", type=int, default=100)
    sub.add_parser("stats")
    a = ap.parse_args()
    {"channel": cmd_channel, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
