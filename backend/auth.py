# auth.py

import os
import json
import pickle
from fastapi import Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# -------------------------------------------------------
# Load OAuth client config from environment
# -------------------------------------------------------
CLIENT_SECRET_JSON = os.getenv("GOOGLE_CLIENT_SECRET_JSON")

if not CLIENT_SECRET_JSON:
    raise Exception("Missing GOOGLE_CLIENT_SECRET_JSON in Render environment!")

client_config = json.loads(CLIENT_SECRET_JSON)

# Backend redirect URL
REDIRECT_URI = "https://mcp-agent-1.onrender.com/auth/callback"


# -------------------------------------------------------
# REQUIRED YOUTUBE SCOPES
# These are necessary for LIKE, COMMENT, SUBSCRIBE
# -------------------------------------------------------
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]


def create_flow():
    """Create OAuth flow with correct YouTube scopes."""
    return Flow.from_client_config(
        client_config,
        scopes=YOUTUBE_SCOPES,
        redirect_uri=REDIRECT_URI
    )


# -------------------------------------------------------
# Save & Load credentials (local only)
# -------------------------------------------------------
def save_creds(creds):
    """Save OAuth credentials locally for development."""
    with open("token.pkl", "wb") as f:
        pickle.dump(creds, f)

    print("\n=========== REFRESH TOKEN ===========")
    print(creds.refresh_token)
    print("=====================================\n")


def load_saved_creds():
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as f:
            return pickle.load(f)
    return None


# -------------------------------------------------------
# Return valid Google OAuth credentials
# -------------------------------------------------------
def get_credentials():
    """
    PRODUCTION:
        Use GOOGLE_REFRESH_TOKEN from Render ENV.
    LOCAL:
        Use token.pkl.
    """
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

    if refresh_token:
        return Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=client_config["web"]["token_uri"],
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"],
            scopes=YOUTUBE_SCOPES
        )

    saved = load_saved_creds()
    if saved:
        return saved

    raise Exception(
        "❌ No valid YouTube OAuth credentials.\n"
        "Visit https://mcp-agent-1.onrender.com/auth/login to authorize your account."
    )


# -------------------------------------------------------
# OAuth Login Route
# -------------------------------------------------------
def login():
    """Redirect user to Google OAuth consent screen."""
    flow = create_flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",   # ensures refresh token
        include_granted_scopes="true"
    )
    return RedirectResponse(auth_url)


# -------------------------------------------------------
# OAuth Callback Route
# -------------------------------------------------------
async def oauth_callback(request: Request):
    """OAuth redirect handler."""
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing OAuth authorization code"}

    flow = create_flow()
    flow.fetch_token(code=code)

    creds = flow.credentials

    # Refresh token is ONLY returned the first time
    if creds.refresh_token:
        save_creds(creds)
        return {
            "message": "✅ OAuth Successful!",
            "refresh_token": creds.refresh_token,
            "instruction": (
                "Add this refresh token to Render → Environment Variables → "
                "GOOGLE_REFRESH_TOKEN"
            )
        }

    return {
        "message": "OAuth successful BUT no refresh token returned.",
        "reason": (
            "Google only returns refresh token on first authorization.\n"
            "To force a new refresh token, append ?prompt=consent to /auth/login."
        )
    }
