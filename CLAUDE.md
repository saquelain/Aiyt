# Shorts loop playbook

Goal: the YouTube channel **delulu content** gets a Short to **1,000 views by 2026-11-01** (10 days from 2026-10-22), then keeps finding what works. The owner gave full freedom over format, topic and language. Everything runs in the cloud; the owner's Mac is not involved. Commit and push straight to `main`.

## Every run

1. Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` (ffmpeg, libcairo and Noto Color Emoji are preinstalled).
2. **Read `LEARNINGS.md` first**, especially "Rules". Never repeat a mistake listed there.
3. `.venv/bin/python run.py stats`, then `run.py retention` (avg % watched; skip if it says unavailable). If auth fails (`invalid_grant`, missing scope), stop and tell the owner the exact error without printing any secret.
4. Judge a video only once it has been public **24h+** (48h is better). Earlier numbers are noise.
5. Update `LEARNINGS.md`: fill in the results table, and write what each result suggests. Any production mistake you hit goes into "Rules" so it never happens again.
6. Daily run only: `run.py plan` gives the format mix (a UCB bandit over formats on log views). Use it as the starting point and override with judgment (a format with 0 views on 4+ judged videos while others get views should go into `strategy.json` → `retired`). Keep **at least one slot per day for something new**: a new format, or a big variation (new hook, new title style, new length, new language such as Hindi/Hinglish, new topic).
7. Make each Short with `run.py make --format F --exp D<day>-<n> --seed <unique>`, then `run.py frames --exp ...` and **look at the PNG** before uploading: text cut off, overlaps, unreadable colours, broken emoji, things stuck. Fix the code, not just the video.
8. Upload with `run.py upload --exp ... [--title ...] --publish-at <UTC>`. Up to `slots_per_day` (6: each upload costs 1,600 of the 10,000 daily API quota units, which reset at midnight Pacific). Spread publish times across the day and rotate which format gets which slot so time-of-day isn't confused with format.
9. Write `reports/YYYY-MM-DD.md` (daily run): views per video, best format so far, what changes tomorrow, progress toward 1,000.
10. Commit `manifest.jsonl`, `stats.jsonl`, `LEARNINGS.md`, `strategy.json`, `reports/` and any code changes; push to `main`.

## Formats (`shortsgen/formats/`)

Each module has `make(out_path, seed, **opts) -> meta`. Add new formats there and to `FORMATS` in `__init__.py`.

| format | what it is | options |
|---|---|---|
| `marble_race` | 8 coloured marbles race down zig-zag ramps, "pick your color" | – |
| `emoji_math` | emoji equations, last line mixes + and × | `think` |
| `odd_emoji` | find the odd emoji, 3 levels | `think` |
| `afterimage` | stare at the dot, inverted picture turns into colour | `scene` (india, france, japan, brazil, landscape, rainbow), `stare` |
| `stop_timer` | pause at exactly X.XX stopwatch | `speed`, `run` |
| `color_word` | Stroop test: say the colour not the word | `words`, `first`, `last` |

## Hard rules

- Never delete videos, never change channel settings, never buy anything.
- No fake engagement, no misleading titles, no reuploads of other people's content, no copyrighted music.
- Every video must be genuinely different (new seed, new content). No near-identical bulk uploads.
- Never commit secrets. Credentials come only from `YT_TOKEN_JSON` (or `YT_CLIENT_ID`/`YT_CLIENT_SECRET`/`YT_REFRESH_TOKEN`). `out/` is git-ignored.
- Keep everything that matters on screen between y=150 and y=1500: YouTube's title, buttons and caption cover the bottom ~400px and the right edge.
