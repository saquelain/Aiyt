"""Run this once on your own computer (it opens a browser) to get a fresh token.

  pip install google-auth-oauthlib
  python auth.py path/to/client_secret.json

It writes token.json (git-ignored). Paste that file's whole contents into the
cloud environment's YT_TOKEN_JSON variable.
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",       # upload + read videos
    "https://www.googleapis.com/auth/yt-analytics.readonly",   # retention / watch time
]

flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1] if len(sys.argv) > 1 else "client_secret.json", SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
open("token.json", "w").write(creds.to_json())
print("wrote token.json; paste its contents into YT_TOKEN_JSON")
