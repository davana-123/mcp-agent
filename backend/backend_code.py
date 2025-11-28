# backend_code.py

import re
from typing import Optional, Dict, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

# -------------------------------------------------------
# Cached YouTube client (improves performance)
# -------------------------------------------------------
_youtube_client = None

def _get_youtube_client():
    global _youtube_client
    if _youtube_client is None:
        creds = get_credentials()
        _youtube_client = build("youtube", "v3", credentials=creds, cache_discovery=False)
    return _youtube_client


# -------------------------------------------------------
# VIDEO ID extraction (kept for compatibility)
# -------------------------------------------------------
def extract_video_id(url: str) -> Optional[str]:
    if not isinstance(url, str):
        return None

    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?#]|$)",
        r"youtu\.be/([0-9A-Za-z_-]{11})(?:[&?#]|$)"
    ]

    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    return None



# -------------------------------------------------------
# Fetch channel ID for subscriptions
# -------------------------------------------------------
def extract_channel_id_from_video(video_id: str) -> Optional[str]:
    try:
        yt = _get_youtube_client()
        resp = yt.videos().list(part="snippet", id=video_id).execute()
        items = resp.get("items", [])
        if not items:
            return None
        return items[0]["snippet"].get("channelId")
    except Exception:
        return None



# -------------------------------------------------------
# SEARCH videos
# -------------------------------------------------------
def search_videos(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    try:
        yt = _get_youtube_client()

        resp = yt.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        ).execute()

        results = []
        for item in resp.get("items", []):
            vid = item["id"].get("videoId")
            snippet = item.get("snippet", {})
            if vid:
                results.append({
                    "videoId": vid,
                    "title": snippet.get("title", ""),
                    "channelTitle": snippet.get("channelTitle", "")
                })

        return results

    except HttpError as e:
        return [{"error": f"Search failed: {e}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]



# -------------------------------------------------------
# LIKE video
# -------------------------------------------------------
def like_video(video_id: str) -> Dict[str, str]:
    if not video_id:
        return {"error": "Missing videoId"}

    try:
        yt = _get_youtube_client()
        yt.videos().rate(id=video_id, rating="like").execute()
        return {"message": "Video liked successfully"}

    except HttpError as e:
        return {"error": f"YouTube API error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



# -------------------------------------------------------
# COMMENT on video
# -------------------------------------------------------
def comment_on_video(video_id: str, text: str) -> Dict[str, str]:
    if not video_id:
        return {"error": "Missing videoId"}
    if not text:
        return {"error": "Missing comment text"}

    try:
        yt = _get_youtube_client()

        yt.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": text}
                    }
                }
            }
        ).execute()

        return {"message": "Comment posted successfully"}

    except HttpError as e:
        return {"error": f"YouTube API error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



# -------------------------------------------------------
# SUBSCRIBE to channel
# -------------------------------------------------------
def subscribe_channel(video_id: str) -> Dict[str, str]:
    if not video_id:
        return {"error": "Missing videoId"}

    channel_id = extract_channel_id_from_video(video_id)
    if not channel_id:
        return {"error": "Unable to fetch channel ID"}

    try:
        yt = _get_youtube_client()

        yt.subscriptions().insert(
            part="snippet",
            body={
                "snippet": {
                    "resourceId": {
                        "kind": "youtube#channel",
                        "channelId": channel_id
                    }
                }
            }
        ).execute()

        return {"message": "Subscribed to channel successfully"}

    except HttpError as e:
        return {"error": f"YouTube API error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



# -------------------------------------------------------
# GET liked videos
# -------------------------------------------------------
def get_liked_videos(max_results: int = 10) -> List[Dict[str, str]]:
    try:
        yt = _get_youtube_client()

        resp = yt.videos().list(
            part="snippet",
            myRating="like",
            maxResults=max_results
        ).execute()

        items = []
        for v in resp.get("items", []):
            items.append({
                "videoId": v.get("id"),
                "title": v["snippet"]["title"],
                "channelTitle": v["snippet"]["channelTitle"]
            })

        return items

    except HttpError as e:
        return [{"error": f"API error: {e}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]



# -------------------------------------------------------
# GET recommended videos
# -------------------------------------------------------
def get_recommended_videos(max_results=10) -> List[Dict[str, str]]:
    liked_videos = get_liked_videos(10)

    if not isinstance(liked_videos, list):
        return []

    recommended = []

    for item in liked_videos:
        title = item.get("title", "")
        keywords = " ".join(title.split()[:4])

        res = search_videos(keywords, 3)
        if isinstance(res, list):
            recommended.extend(res)

    # Deduplicate
    unique = {}
    for r in recommended:
        if r["videoId"] not in unique:
            unique[r["videoId"]] = r

    return list(unique.values())[:max_results]
