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

# ALWAYS use backend URL for redirect
REDIRECT_URI = "https://mcp-agent-1.onrender.com/auth/callback"


# -------------------------------------------------------
# Create OAuth flow with FULL YouTube scope
# -------------------------------------------------------
def create_flow():
    return Flow.from_client_config(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/youtube"   # FULL READ/WRITE SCOPE
        ],
        redirect_uri=REDIRECT_URI
    )


# -------------------------------------------------------
# Save & Load credentials (local only for DEV)
# -------------------------------------------------------
def save_creds(creds):
    """
    Save OAuth credentials to token.pkl.
    This is used only for local development—not on Render.
    """
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
# Main function to return valid Google OAuth credentials
# -------------------------------------------------------
def get_credentials():
    """
    Production: Use refresh token from Render ENV.
    Local: Use token.pkl.
    """
    refresh = os.getenv("GOOGLE_REFRESH_TOKEN")

    if refresh:
        return Credentials(
            token=None,
            refresh_token=refresh,
            token_uri=client_config["web"]["token_uri"],
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"]
        )

    saved = load_saved_creds()
    if saved:
        return saved

    raise Exception("❌ No valid YouTube OAuth credentials. Visit /auth/login.")


# -------------------------------------------------------
# OAuth: Login & Callback Routes
# -------------------------------------------------------
def login():
    """
    Redirect user to Google OAuth screen.
    """
    flow = create_flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    return RedirectResponse(auth_url)


async def oauth_callback(request: Request):
    """
    Called after user approves permissions.
    """
    code = request.query_params.get("code")

    flow = create_flow()
    flow.fetch_token(code=code)

    creds = flow.credentials

    # Only returned during first authorization
    if creds.refresh_token:
        save_creds(creds)

        return {
            "message": "OAuth successful!",
            "next_step": "Copy the refresh token from Render logs → store in Render ENV as GOOGLE_REFRESH_TOKEN"
        }

    return {
        "message": "OAuth successful BUT refresh token missing.",
        "reason": "Google did not provide a new refresh token. Remove stored token and re-auth with ?prompt=consent"
    }
