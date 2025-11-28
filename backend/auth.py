# auth.py
import os
import json
import pickle
from fastapi import Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

GOOGLE_CLIENT_SECRET_JSON = os.environ.get("GOOGLE_CLIENT_SECRET_JSON")
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN")

# Load JSON
client_config = json.loads(GOOGLE_CLIENT_SECRET_JSON)

# Create OAuth flow
flow = Flow.from_client_config(
    client_config,
    scopes=[
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube.readonly"
    ],
    redirect_uri=client_config["web"]["redirect_uris"][0]
)

# Save credentials
def save_creds(creds):
    with open("token.pkl", "wb") as f:
        pickle.dump(creds, f)

    # Print refresh token so user can store in Render ENV
    print("\n\n====================================")
    print(" REFRESH TOKEN GENERATED:")
    print(creds.refresh_token)
    print("====================================\n\n")


def load_saved_creds():
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as f:
            return pickle.load(f)
    return None


def get_credentials():
    # Prefer permanent refresh token from Render ENV
    if GOOGLE_REFRESH_TOKEN:
        return Credentials(
            token=None,
            refresh_token=GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"]
        )

    # Otherwise use saved token.pkl
    creds = load_saved_creds()
    if creds:
        return creds

    raise Exception("No credentials available — login required!")


# ---------------------- ROUTES -------------------------

def login():
    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    flow.fetch_token(code=code)

    creds = flow.credentials

    if creds.refresh_token:
        save_creds(creds)

    return {"message": "Login successful! Now copy refresh token from logs."}
