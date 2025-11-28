# server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from auth import login, oauth_callback
from backend_code import (
    search_videos,
    get_liked_videos,
    get_recommended_videos,
    like_video,
    comment_on_video,
    subscribe_channel
)

app = FastAPI(title="YouTube MCP Agent Backend")

# -------------------------------------------------------
# CORS CONFIG
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Allow Vercel frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Pydantic Request Models
# -------------------------------------------------------
class LikeRequest(BaseModel):
    videoId: str

class CommentRequest(BaseModel):
    videoId: str
    text: str

class SubscribeRequest(BaseModel):
    videoId: str   # We extract channelId internally


# -------------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------------
@app.get("/auth/login")
def auth_login():
    return login()

@app.get("/auth/callback")
async def auth_callback(request):
    return await oauth_callback(request)


# -------------------------------------------------------
# YOUTUBE READ ROUTES
# -------------------------------------------------------
@app.get("/api/search")
def api_search(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    return search_videos(query)


@app.get("/api/liked")
def api_liked():
    return get_liked_videos()


@app.get("/api/recommend")
def api_recommend():
    return get_recommended_videos()


# -------------------------------------------------------
# YOUTUBE WRITE ROUTES (POST)
# -------------------------------------------------------
@app.post("/api/like")
def api_like(req: LikeRequest):
    return like_video(req.videoId)


@app.post("/api/comment")
def api_comment(req: CommentRequest):
    return comment_on_video(req.videoId, req.text)


@app.post("/api/subscribe")
def api_subscribe(req: SubscribeRequest):
    return subscribe_channel(req.videoId)


# -------------------------------------------------------
# LOCAL DEV
# -------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
