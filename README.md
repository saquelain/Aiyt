# Aiyt

Automated YouTube Shorts experiment for the channel **delulu content**. Goal: one Short at 1,000 views within 10 days of 2026-10-22. Each day it posts several Shorts in different formats, tracks views, and shifts toward what works. `CLAUDE.md` is the playbook and `LEARNINGS.md` is the running log.

## Setup

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run.py channel
.venv/bin/python run.py make --format emoji_math --exp test --seed 1 && .venv/bin/python run.py frames --exp test
```

Needs `ffmpeg`, libcairo and the Noto Color Emoji font. Credentials come only from the environment: `YT_TOKEN_JSON` (the whole contents of an OAuth token.json). To get a fresh token with no local computer: `python auth.py url`, approve in any browser, then `python auth.py code "<the localhost URL>"`.
