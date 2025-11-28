# server.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI()

# Allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- AUTH ROUTES ----------
@app.get("/login")
def login_route():
    return login()

@app.get("/oauth2callback")
async def oauth_callback_route(request: Request):
    return await oauth_callback(request)


# ---------- API ROUTES ----------
@app.get("/search")
def search(query: str):
    return search_videos(query)

@app.get("/liked")
def liked():
    return get_liked_videos()

@app.get("/recommend")
def recommend():
    return get_recommended_videos()

@app.get("/like")
def like(videoUrl: str):
    return like_video(videoUrl)

@app.get("/comment")
def comment(videoUrl: str, text: str):
    return comment_on_video(videoUrl, text)

@app.get("/subscribe")
def subscribe(videoUrl: str):
    return subscribe_channel(videoUrl)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
