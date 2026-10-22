"""Get a fresh YouTube token without a local computer.

  python auth.py url              # prints a Google sign-in link; open it on any device
  python auth.py code '<URL>'     # paste the localhost URL the browser ends up on

Approving sends the browser to http://localhost/?code=..., which fails to load:
that's expected, the code is in the address bar. Uses the client id/secret from
YT_TOKEN_JSON (or YT_CLIENT_ID / YT_CLIENT_SECRET) and writes the new token.json
to the path in AUTH_OUT (default out/token.json, git-ignored). Paste that file's
contents into the environment's YT_TOKEN_JSON.
"""
import json
import os
import sys
import urllib.parse

from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",       # upload + read videos
    "https://www.googleapis.com/auth/yt-analytics.readonly",   # retention / watch time
]
REDIRECT = "http://localhost:8080/"


def flow():
    if os.environ.get("YT_TOKEN_JSON"):
        t = json.loads(os.environ["YT_TOKEN_JSON"])
        cid, secret = t["client_id"], t["client_secret"]
    else:
        cid, secret = os.environ["YT_CLIENT_ID"], os.environ["YT_CLIENT_SECRET"]
    cfg = {"installed": {"client_id": cid, "client_secret": secret,
                         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                         "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": [REDIRECT]}}
    return Flow.from_client_config(cfg, SCOPES, redirect_uri=REDIRECT, autogenerate_code_verifier=False)


if sys.argv[1] == "url":
    url, _ = flow().authorization_url(access_type="offline", prompt="consent")
    print(url)
else:
    arg = sys.argv[2]
    code = urllib.parse.parse_qs(urllib.parse.urlparse(arg).query).get("code", [arg])[0]
    f = flow()
    f.fetch_token(code=code)
    out = os.environ.get("AUTH_OUT", "out/token.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(f.credentials.to_json())
    print("scopes:", f.credentials.scopes, "\nwrote", out)
