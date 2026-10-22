# Aiyt

Automated YouTube Shorts experiment for the channel "content delulu". Goal: 1,000 views on one Short within 10 days of 2026-10-22, posting several different formats each day and learning from the numbers.

## Setup

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run.py channel
```

Needs `ffmpeg` and libcairo. Credentials come only from the environment: `YT_TOKEN_JSON` (the whole contents of an OAuth token.json), or `YT_CLIENT_ID`, `YT_CLIENT_SECRET` and `YT_REFRESH_TOKEN`. To get a fresh token, run `python auth.py client_secret.json` on your own computer.
