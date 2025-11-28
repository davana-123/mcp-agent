# auth.py
import os
import json
import pickle
from fastapi import Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# -------------------------------------------------------
# Load OAuth client config from environment (Render ENV)
# -------------------------------------------------------
CLIENT_SECRET_JSON = os.getenv("GOOGLE_CLIENT_SECRET_JSON")

if not CLIENT_SECRET_JSON:
    raise Exception("Missing GOOGLE_CLIENT_SECRET_JSON in Render environment!")

client_config = json.loads(CLIENT_SECRET_JSON)

REDIRECT_URI = "https://mcp-agent-1.onrender.com/auth/callback"


# -------------------------------------------------------
# Utility: Create OAuth Flow dynamically (IMPORTANT)
# -------------------------------------------------------
def create_flow():
    return Flow.from_client_config(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.readonly"
        ],
        redirect_uri=REDIRECT_URI
    )


# -------------------------------------------------------
# Save & Load creds (local token.pkl only for DEV)
# -------------------------------------------------------
def save_creds(creds):
    """Save credentials to token.pkl (dev use)"""
    with open("token.pkl", "wb") as f:
        pickle.dump(creds, f)

    print("\n=========== REFRESH TOKEN ===========")
    print(creds.refresh_token)
    print("=====================================\n")


def load_saved_creds():
    """Load saved credentials"""
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as f:
            return pickle.load(f)
    return None


# -------------------------------------------------------
# Main: Return valid usable credentials
# -------------------------------------------------------
def get_credentials():
    """Central method to fetch valid credentials"""

    # 1. Production mode: Prefer refresh token stored in ENV
    refresh = os.getenv("GOOGLE_REFRESH_TOKEN")

    if refresh:
        return Credentials(
            token=None,
            refresh_token=refresh,
            token_uri=client_config["web"]["token_uri"],
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"]
        )

    # 2. Development fallback
    saved = load_saved_creds()
    if saved:
        return saved

    raise Exception("No YouTube OAuth credentials found. Visit /auth/login.")


# -------------------------------------------------------
# Routes
# -------------------------------------------------------
def login():
    """Redirect user to Google OAuth screen."""
    flow = create_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(auth_url)


async def oauth_callback(request: Request):
    """Handle Google OAuth callback."""
    code = request.query_params.get("code")

    flow = create_flow()
    flow.fetch_token(code=code)

    creds = flow.credentials

    # Only the FIRST login generates refresh_token
    if creds.refresh_token:
        save_creds(creds)

        return {
            "message": "OAuth successful!",
            "next_step": "Copy the refresh token from Render logs → store in Render ENV as GOOGLE_REFRESH_TOKEN"
        }

    return {
        "message": "OAuth successful BUT refresh token missing.",
        "reason": "Google didn't issue a new refresh token. Remove saved credentials & retry using ?prompt=consent"
    }
