**🚀 YouTube MCP Agent**
**AI-Powered YouTube Automation using Model Context Protocol (MCP)**

This project implements a fully functional AI agent capable of interacting with YouTube through a custom-built MCP server.
The agent can search videos, fetch liked videos, recommend videos, and even like, comment, and subscribe — all via YouTube Data API v3.

A modern web UI (YouTube-style) is provided to demonstrate the MCP tools.

📌Features

🔍 Retrieval Tools

Search YouTube videos
Fetch user's liked videos
Generate smart recommendations based on liked content

⚡Action Tools

Like a YouTube video
Post a comment
Subscribe to a channel

🎨 Frontend (Vercel)

YouTube-style interface
Search bar with Enter key support
Clickable video cards (open directly on YouTube)
Sidebar navigation
Pop-up/inline acknowledgments after actions

🔐 Security

Google OAuth2 login
Refresh token system
Credentials stored safely in environment variables

🌐 Live Demo Links
Frontend (Vercel)

👉 https://mcp-agent-gamma.vercel.app

Backend API (Render)

👉 https://mcp-agent-1.onrender.com

🛠️ Tech Stack
Frontend

HTML

CSS

JavaScript

Vercel deployment

Backend

FastAPI (Python)

Google API Client

OAuth2 Authorization

Render deployment

Protocol

Model Context Protocol (MCP)


🏗️ Architecture Overview

User Interface (Vercel)
        │
        ▼
Frontend JS (fetch API)
        │
        ▼
MCP Backend Server (FastAPI)
        │
        ▼
Google OAuth2 (Refresh Token)
        │
        ▼
YouTube Data API v3

📁 Project Structure
mcp-agent/
│
├── backend/
│   ├── server.py         # FastAPI MCP server
│   ├── backend_code.py   # YouTube MCP tool functions
│   ├── auth.py           # OAuth logic
│   ├── requirements.txt
│   └── token.pkl         # (local use only)
│
├── frontend/
│   ├── index.html        # Frontend UI
│
└── README.md

🔧 Installation & Setup
1. Clone repository
git clone https://github.com/your-username/mcp-agent
cd mcp-agent

🖥️ Backend Setup
2. Install dependencies
cd backend
pip install -r requirements.txt

3. Create environment variables

Create a .env file:

GOOGLE_CLIENT_SECRET_JSON=<Your Google OAuth client JSON>
GOOGLE_REFRESH_TOKEN=<Refresh token>

4. Run backend locally
uvicorn server:app --host 0.0.0.0 --port 8000


Backend will run at:

http://localhost:8000

🔑 OAuth Setup (Required)

Go to Google Cloud Console

Create a project

Enable YouTube Data API v3

Create OAuth Client ID → Web Application

Add authorized redirect URI:

https://mcp-agent-1.onrender.com/auth/callback


Visit:

https://mcp-agent-1.onrender.com/auth/login


Approve access

Copy refresh token from server logs

Add it to Render environment:

GOOGLE_REFRESH_TOKEN=your_token


Done. Now ALL YouTube actions will work.

🧪 API Endpoints (MCP Tools)
Action	Method	Endpoint	Description
Search videos	GET	/api/search?query=...	Returns search results
Liked videos	GET	/api/liked	Fetches liked videos
Recommended videos	GET	/api/recommend	Generates recommendations
Like a video	POST	/api/like	Likes a video
Comment on video	POST	/api/comment	Adds a comment
Subscribe	POST	/api/subscribe	Subscribes to channel
📦 Frontend Setup

If you modify UI:

Run locally:

Just open:

frontend/index.html


To deploy:

Upload to Vercel

🧭 Usage

Open frontend

Search any video

Click video → opens on YouTube

Use:

👍 Like

💬 Comment

🔔 Subscribe

This project successfully demonstrates a fully functional AI-driven YouTube MCP Agent, integrating the MCP protocol, FastAPI backend, secure OAuth2 authentication, and a modern YouTube-style frontend UI.

Everything is live, operational, and production-ready.
