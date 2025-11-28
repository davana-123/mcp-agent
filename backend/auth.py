# auth.py
import os
import json
import pickle
from fastapi import Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Load client secret JSON from environment
CLIENT_SECRET_JSON = os.getenv("GOOGLE_CLIENT_SECRET_JSON")

if not CLIENT_SECRET_JSON:
    raise Exception("Missing GOOGLE_CLIENT_SECRET_JSON in Render environment!")

client_config = json.loads(CLIENT_SECRET_JSON)

# OAuth flow
flow = Flow.from_client_config(
    client_config,
    scopes=[
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube.readonly"
    ],
    redirect_uri=client_config["web"]["redirect_uris"][0]
)

def save_creds(creds):
    """Save credentials permanently on Render filesystem"""
    with open("token.pkl", "wb") as f:
        pickle.dump(creds, f)

    print("\n==============================")
    print("REFRESH TOKEN GENERATED:")
    print(creds.refresh_token)
    print("==============================\n")

def load_saved_creds():
    """Load saved credentials if available"""
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as f:
            return pickle.load(f)
    return None


def get_credentials():
    """Central method to fetch valid credentials"""
    refresh = os.getenv("GOOGLE_REFRESH_TOKEN")

    # If refresh token is stored in Render ENV
    if refresh:
        return Credentials(
            token=None,
            refresh_token=refresh,
            token_uri=client_config["web"]["token_uri"],
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"]
        )

    # If token.pkl exists (generated from /login)
    saved = load_saved_creds()
    if saved:
        return saved

    raise Exception("❌ No credentials found. Please login using /login")


# -------------------- ROUTES --------------------

def login():
    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)

async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    flow.fetch_token(code=code)

    creds = flow.credentials

    # Save refresh token (only first login generates)
    if creds.refresh_token:
        save_creds(creds)

    return {"message": "Login successful! Check Render logs for your refresh token."}
