# server.py

from fastapi import FastAPI, HTTPException, Request
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

# -------------------------------------------------------
# FASTAPI APP
# -------------------------------------------------------
app = FastAPI(title="YouTube MCP Agent Backend")

# -------------------------------------------------------
# CORS CONFIG (IMPORTANT FOR FRONTEND)
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# REQUEST MODELS
# -------------------------------------------------------
class LikeRequest(BaseModel):
    videoId: str

class CommentRequest(BaseModel):
    videoId: str
    text: str

class SubscribeRequest(BaseModel):
    videoId: str   # Channel ID extracted in backend_code.py


# -------------------------------------------------------
# AUTH ROUTES (GOOGLE OAUTH)
# -------------------------------------------------------
@app.get("/auth/login")
def auth_login():
    """
    Redirects user to Google OAuth Permission Screen.
    """
    return login()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """
    Google redirects back here with ?code=XXXXX.
    Must accept Request as a typed FastAPI Request.
    """
    return await oauth_callback(request)


# -------------------------------------------------------
# YOUTUBE SEARCH
# -------------------------------------------------------
@app.get("/api/search")
def api_search(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")
    return search_videos(query)


# -------------------------------------------------------
# LIKED VIDEOS
# -------------------------------------------------------
@app.get("/api/liked")
def api_liked():
    return get_liked_videos()


# -------------------------------------------------------
# RECOMMENDED VIDEOS
# -------------------------------------------------------
@app.get("/api/recommend")
def api_recommend():
    return get_recommended_videos()


# -------------------------------------------------------
# LIKE VIDEO
# -------------------------------------------------------
@app.post("/api/like")
def api_like(req: LikeRequest):
    return like_video(req.videoId)


# -------------------------------------------------------
# COMMENT VIDEO
# -------------------------------------------------------
@app.post("/api/comment")
def api_comment(req: CommentRequest):
    return comment_on_video(req.videoId, req.text)


# -------------------------------------------------------
# SUBSCRIBE CHANNEL
# -------------------------------------------------------
@app.post("/api/subscribe")
def api_subscribe(req: SubscribeRequest):
    return subscribe_channel(req.videoId)


# -------------------------------------------------------
# FOR LOCAL DEVELOPMENT
# -------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
