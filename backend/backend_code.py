# youtube_api.py
import re
import socket
from typing import Optional, Any, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

def _get_youtube_client():
    creds = get_credentials()
    return build("youtube", "v3", credentials=creds)

def extract_video_id(url: str) -> Optional[str]:
    if not isinstance(url, str):
        return None
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&\?#]|$)",
        r"youtu\.be\/([0-9A-Za-z_-]{11})(?:[&\?#]|$)"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def extract_channel_id_from_video(video_id: str) -> Optional[str]:
    try:
        youtube = _get_youtube_client()
        resp = youtube.videos().list(part="snippet", id=video_id).execute()
        items = resp.get("items", [])
        if not items:
            return None
        return items[0]["snippet"].get("channelId")
    except Exception:
        return None

def search_videos(query: str, max_results: int = 5) -> Any:
    try:
        youtube = _get_youtube_client()
        response = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        ).execute()

        results = []
        for item in response.get("items", []):
            vid = item["id"].get("videoId")
            snippet = item.get("snippet", {})
            if vid:
                results.append({
                    "videoId": vid,
                    "title": snippet.get("title", ""),
                    "channelTitle": snippet.get("channelTitle", "")
                })
        return results

    except Exception as e:
        return {"error": str(e)}

def like_video(video_url: str) -> Dict[str, str]:
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"error": "Invalid video URL"}

    try:
        youtube = _get_youtube_client()
        youtube.videos().rate(id=video_id, rating="like").execute()
        return {"message": "👍 Video liked successfully."}
    except Exception as e:
        return {"error": str(e)}

def comment_on_video(video_url: str, text: str) -> Dict[str, str]:
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"error": "Invalid video URL"}
    if not text:
        return {"error": "Comment text is required"}

    try:
        youtube = _get_youtube_client()
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": text}}
                }
            }
        ).execute()
        return {"message": "💬 Comment posted."}
    except Exception as e:
        return {"error": str(e)}

def subscribe_channel(video_url: str) -> Dict[str, str]:
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"error": "Invalid video URL"}
    channel_id = extract_channel_id_from_video(video_id)
    if not channel_id:
        return {"error": "Unable to detect channel ID"}

    try:
        youtube = _get_youtube_client()
        youtube.subscriptions().insert(
            part="snippet",
            body={
                "snippet": {
                    "resourceId": {"kind": "youtube#channel", "channelId": channel_id}
                }
            }
        ).execute()
        return {"message": "🔔 Subscribed successfully."}
    except Exception as e:
        return {"error": str(e)}

def get_liked_videos(max_results: int = 10) -> Any:
    try:
        youtube = _get_youtube_client()
        resp = youtube.videos().list(
            part="snippet",
            myRating="like",
            maxResults=max_results
        ).execute()

        items = []
        for item in resp.get("items", []):
            items.append({
                "videoId": item.get("id"),
                "title": item["snippet"]["title"],
                "channelTitle": item["snippet"]["channelTitle"]
            })
        return items
    except Exception as e:
        return {"error": str(e)}

def get_recommended_videos(max_results=10):
    liked = get_liked_videos(10)
    if isinstance(liked, dict):
        return liked

    recommended = []
    for v in liked:
        title = v["title"]
        keywords = " ".join(title.split()[:4])
        results = search_videos(keywords, 3)
        if isinstance(results, list):
            recommended.extend(results)

    unique = []
    seen = set()
    for r in recommended:
        vid = r["videoId"]
        if vid not in seen:
            seen.add(vid)
            unique.append(r)
        if len(unique) >= max_results:
            break

    return unique
