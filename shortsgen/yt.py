"""YouTube Data API access. Credentials come only from environment variables:

  YT_TOKEN_JSON   the full contents of an OAuth token.json, or
  YT_CLIENT_ID + YT_CLIENT_SECRET + YT_REFRESH_TOKEN
"""
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def creds():
    if os.environ.get("YT_TOKEN_JSON"):
        c = Credentials.from_authorized_user_info(json.loads(os.environ["YT_TOKEN_JSON"]))
    else:
        missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
        if missing:
            raise SystemExit("no credentials: set YT_TOKEN_JSON or " + ", ".join(missing))
        c = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"])
    if not c.valid:
        c.refresh(Request())
    return c


_api = None


def api():
    global _api
    if _api is None:
        _api = build("youtube", "v3", credentials=creds(), cache_discovery=False)
    return _api


def upload(path, title, description, tags, publish_at=None, category="24"):
    """Upload a video. With publish_at (RFC3339 UTC) it stays private until then."""
    status = {"selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}
    if publish_at:
        status.update(privacyStatus="private", publishAt=publish_at)
    else:
        status["privacyStatus"] = "public"
    body = {"snippet": {"title": title, "description": description, "tags": tags, "categoryId": category},
            "status": status}
    req = api().videos().insert(part="snippet,status", body=body,
                                media_body=MediaFileUpload(path, chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]


def channel_uploads(limit=50):
    ch = api().channels().list(part="contentDetails,snippet,statistics", mine=True).execute()["items"][0]
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    items, token = [], None
    while len(items) < limit:
        r = api().playlistItems().list(part="contentDetails,snippet", playlistId=pl,
                                       maxResults=min(50, limit - len(items)), pageToken=token).execute()
        items += [(i["contentDetails"]["videoId"], i["snippet"]["title"]) for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    return ch, items


def stats(video_ids):
    out = {}
    for i in range(0, len(video_ids), 50):
        r = api().videos().list(part="statistics,status,snippet,contentDetails",
                                id=",".join(video_ids[i:i + 50])).execute()
        for v in r["items"]:
            s = v["statistics"]
            out[v["id"]] = {
                "title": v["snippet"]["title"],
                "published": v["snippet"].get("publishedAt"),
                "privacy": v["status"]["privacyStatus"],
                "publishAt": v["status"].get("publishAt"),
                "duration": v["contentDetails"].get("duration"),
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
            }
    return out


def retention(video_ids, start, end):
    """Per-video views, average seconds watched and average % watched (Analytics lags 1-3 days)."""
    yta = build("youtubeAnalytics", "v2", credentials=creds(), cache_discovery=False)
    r = yta.reports().query(ids="channel==MINE", startDate=start, endDate=end, dimensions="video",
                            metrics="views,averageViewDuration,averageViewPercentage",
                            filters="video==" + ",".join(video_ids)).execute()
    return {row[0]: {"views": row[1], "avg_s": row[2], "avg_pct": row[3]} for row in r.get("rows", [])}
