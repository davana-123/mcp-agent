# backend_code.py

import re
from typing import Optional, Dict, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials


# -------------------------------------------------------
# Create YouTube client using valid OAuth credentials
# -------------------------------------------------------
def _youtube():
    """
    Always rebuild the YouTube API client with fresh credentials.
    """
    try:
        creds = get_credentials()
        return build(
            "youtube",
            "v3",
            credentials=creds,
            cache_discovery=False
        )
    except Exception as e:
        return None


# -------------------------------------------------------
# Extract 11-digit YouTube video ID
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

    # Already a valid video ID?
    if len(url) == 11:
        return url

    return None


# -------------------------------------------------------
# Fetch channelId from a video
# -------------------------------------------------------
def extract_channel_id_from_video(video_id: str) -> Optional[str]:
    try:
        yt = _youtube()
        if yt is None:
            return None

        resp = yt.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        items = resp.get("items", [])
        if not items:
            return None

        return items[0]["snippet"]["channelId"]

    except Exception:
        return None


# -------------------------------------------------------
# SEARCH videos
# -------------------------------------------------------
def search_videos(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    try:
        yt = _youtube()
        if yt is None:
            return [{"error": "OAuth not initialized. Visit /auth/login"}]

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
        return [{"error": f"YouTube API error: {e.error_details}"}]

    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]


# -------------------------------------------------------
# LIKE video
# -------------------------------------------------------
def like_video(video_id: str) -> Dict[str, str]:
    try:
        yt = _youtube()
        if yt is None:
            return {"error": "Missing OAuth credentials. Re-login using /auth/login"}

        yt.videos().rate(id=video_id, rating="like").execute()
        return {"message": "👍 Video liked successfully"}

    except HttpError as e:
        return {"error": f"YouTube error: {e.error_details}"}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------------
# COMMENT on video
# -------------------------------------------------------
def comment_on_video(video_id: str, text: str) -> Dict[str, str]:
    if not text:
        return {"error": "Comment text cannot be empty"}

    try:
        yt = _youtube()
        if yt is None:
            return {"error": "Missing OAuth credentials. Re-login using /auth/login"}

        yt.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": text
                        }
                    }
                }
            }
        ).execute()

        return {"message": "💬 Comment posted successfully"}

    except HttpError as e:
        return {"error": f"YouTube error: {e.error_details}"}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------------
# SUBSCRIBE to channel (auto extract from videoId)
# -------------------------------------------------------
def subscribe_channel(video_id: str) -> Dict[str, str]:
    try:
        channel_id = extract_channel_id_from_video(video_id)
        if not channel_id:
            return {"error": "Unable to find a channel for this video."}

        yt = _youtube()
        if yt is None:
            return {"error": "Missing OAuth credentials. Re-login using /auth/login"}

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

        return {"message": "🔔 Subscribed successfully"}

    except HttpError as e:
        return {"error": f"YouTube error: {e.error_details}"}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------------
# GET liked videos
# -------------------------------------------------------
def get_liked_videos(max_results: int = 10) -> List[Dict[str, str]]:
    try:
        yt = _youtube()
        if yt is None:
            return [{"error": "Missing OAuth credentials. Re-login using /auth/login"}]

        resp = yt.videos().list(
            part="snippet",
            myRating="like",
            maxResults=max_results
        ).execute()

        results = []
        for v in resp.get("items", []):
            results.append({
                "videoId": v["id"],
                "title": v["snippet"]["title"],
                "channelTitle": v["snippet"]["channelTitle"]
            })

        return results

    except HttpError as e:
        return [{"error": f"YouTube error: {e.error_details}"}]

    except Exception as e:
        return [{"error": str(e)}]


# -------------------------------------------------------
# RECOMMEND videos based on liked videos
# -------------------------------------------------------
def get_recommended_videos(max_results=10) -> List[Dict[str, str]]:
    liked = get_liked_videos(10)

    if not isinstance(liked, list):
        return []

    recommended = []

    for item in liked:
        title = item.get("title", "")
        keywords = " ".join(title.split()[:4])

        # Search based on keywords extracted from liked titles
        results = search_videos(keywords, 3)
        if isinstance(results, list):
            recommended.extend(results)

    # Deduplicate results
    unique = {}
    for r in recommended:
        if r["videoId"] not in unique:
            unique[r["videoId"]] = r

    return list(unique.values())[:max_results]
