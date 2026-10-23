# Learnings

Read this before every run. Add to it after every run.

## Rules (mistakes already made; never repeat them)

1. Cairo's text API can't draw emoji (they become boxes). Put emoji only in titles, or draw them with `canvas.emoji()`.
2. Emoji placed 160px apart at 120px size overlap the operators between them. Leave ≥200px between emoji centres when there's a symbol between them.
3. Similar colours break colour games: ORANGE vs RED and PINK vs PURPLE read the same on a phone. `color_word` uses only RED, BLUE, GREEN, YELLOW, PURPLE.
4. Bumpers placed less than a ball-diameter above a ramp wedge marbles in place for the whole race. Bumpers now sit in the drop holes, and `marble_race` rejects any sim where a marble stops moving (`stuck()`).
5. Obstacles drawn in the same colour as a player (orange bumpers next to an orange marble) confuse viewers. Scenery must use colours no player uses.
6. YouTube's UI covers the bottom ~400px. Countdowns and calls to action belong above y≈1500.
7. `cairo` crashes on a zero scale. Animations that start at size 0 must skip drawing (`emoji()` does).
8. Several `run.py make` running in parallel used to race on `manifest.jsonl`. It now takes a file lock; keep it.
10. **YouTube caps uploads per channel**, separately from the API quota. On 10-23 the 5th upload failed with `uploadLimitExceeded` after 10 uploads in about 12 hours. Keep batches 24h apart (the daily run does) and never more than 6 in a rolling 24h. Phone-verifying the channel (youtube.com/verify) raises the cap.
11. Scheduled runs read the login from the environment's `YT_TOKEN_JSON`, not from any session's files. On 10-22/23 the env still had the dead August token, so both scheduled runs stopped at `invalid_grant`.
12. Everything visible must stay above y≈1500, including countdown numbers and end text. odd_emoji and emoji_math broke this on day 1 and were moved up on day 2.
9. Always check that a puzzle's printed answer is correct (emoji_math computes it with `eval` of the same expression it draws). Recheck after any change to the question order.

## Baseline (before this pipeline)

- 6 public Shorts from 2026-10-21/22 (escape-the-rings physics sims, one odd-one-out) had **1–5 views each** after a day. Older narrated "What If"/history videos got 0–14 views. Older Valorant clips got 400–2,000 views, so real, watchable moments beat slideshows. Those older videos are private.

## Experiments

Day 1 tests six formats at once, one each, at different times, to find a direction fast.

| exp | format | publish (UTC) | title | views @24h | views @48h | notes |
|---|---|---|---|---|---|---|
| D1-1 | marble_race | 10-22 20:50 | Marble race: comment your color 👇 | | | 20s, 13 lead changes |
| D1-2 | emoji_math | 10-22 22:30 | Most people get this WRONG 😳 | | | answer 45 (3+7×6) |
| D1-3 | odd_emoji | 10-23 00:30 | Can you find the different emoji? 🔍 | | | 3 levels, 22s |
| D1-4 | afterimage | 10-23 02:30 | Stare at the dot for 15 seconds… 🤯 | | | Indian flag |
| D1-5 | stop_timer | 10-23 04:30 | Pause at exactly 7.16 ⏱️ (I bet you can't) | | | 9s, loops |
| D1-6 | color_word | 10-23 06:30 | Only 1% can finish this brain test 😵 | | | 16 words |
| D2-3 | stop_timer | 10-23 09:30 | Stop the timer at 10.30 😤 | | | faster: speed 1.5 |
| D2-6 | color_word | 10-23 12:00 | Your brain will glitch at the end 🧠 | | | shorter: 12 words, 15s |
| D2-2 | emoji_math | 10-23 14:00 | Sirf 1% log solve kar paate hain 🧠 | | | NEW: Hinglish, India prime time |
| D2-4 | odd_emoji | 10-23 16:00 | Alag emoji dhundo 👀 Level 3 impossible hai | | | NEW: Hinglish, India prime time |
| D2-1 | marble_race | not uploaded | | | | hit upload cap; re-make with the same seed (31) to post |
| D2-5 | afterimage | not uploaded | | | | hit upload cap; landscape scene, seed 35 |

## What the data says so far

- 10-23 07:40 UTC (videos 1–11h old): D1-1 marble_race 3 views, all other day-1 Shorts 0. Too early to judge. Note: brand-new Shorts on this channel are getting almost no first-hour impressions, so distribution is the bottleneck, not just the format.

## Ideas queue (try when a slot frees up)

- Hindi/Hinglish versions of the best-performing format (big audience, less competition).
- "Which one are you?" / "pick a box" choice videos (comment bait without being misleading).
- Ball battle sims ("which color survives"), satisfying loops under 10s (rewatch rate).
- Countdown "guess the emoji movie/song" quizzes.
- Same winning format with three different title hooks to test titles alone.
