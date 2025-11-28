# server.py
from fastapi import FastAPI, Request, HTTPException
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

app = FastAPI(title="YouTube MCP Agent Backend")

# ------------ CORS (REQUIRED FOR VERCEL + RENDER) ------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mcp-agent-gamma.vercel.app",
        "https://mcp-agent-13y5wia0i-davana-s-projects.vercel.app",
        "*"  # temporary until testing is complete
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ AUTH ROUTES ------------
@app.get("/auth/login")
def auth_login():
    """
    Redirects user to Google OAuth screen.
    """
    return login()

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """
    Handles the OAuth callback from Google.
    """
    return await oauth_callback(request)


# ------------ YOUTUBE API ROUTES (MCP Tools) ------------

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

@app.post("/api/like")
def api_like(videoId: str):
    return like_video(videoId)

@app.post("/api/comment")
def api_comment(videoId: str, text: str):
    return comment_on_video(videoId, text)

@app.post("/api/subscribe")
def api_subscribe(channelId: str):
    return subscribe_channel(channelId)


# ------------ RUN LOCALLY ------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
