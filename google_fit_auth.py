#!/usr/bin/env python3
"""
Google Fit OAuth authorization.
"""

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from env_utils import load_dotenv

load_dotenv()

# Scopes needed for fitness data (read-only).
SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "https://www.googleapis.com/auth/fitness.heart_rate.read",
    "https://www.googleapis.com/auth/fitness.location.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.nutrition.read",
]

CREDENTIALS_FILE = os.environ.get(
    "GOOGLE_CREDENTIALS_FILE",
    "credentials/google-fit-credentials.json",
)
TOKEN_FILE = os.environ.get("TOKEN_PATH", "credentials/google-fit-token.json")


def save_credentials(creds):
    """Persist OAuth credentials to the configured token path."""
    token_path = Path(TOKEN_FILE)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")


def main():
    creds = None
    credentials_path = Path(CREDENTIALS_FILE)
    token_path = Path(TOKEN_FILE)

    if token_path.exists():
        print(f"Loading existing token from {TOKEN_FILE}")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.valid:
        print("Token already valid. Ready to use.")
        return creds

    if creds and creds.expired and creds.refresh_token:
        print("Refreshing expired token...")
        creds.refresh(Request())
        save_credentials(creds)
        print("Token refreshed.")
        return creds

    print("Starting OAuth flow...")
    if not credentials_path.exists():
        print(f"ERROR: {CREDENTIALS_FILE} not found.")
        return None

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(
            port=0,
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

        save_credentials(creds)

        print(f"Token saved to {TOKEN_FILE}")
        print("Ready to access Google Fit API.")
        print(f"Token expires: {creds.expiry}")
        print(f"Refresh token: {'Yes' if creds.refresh_token else 'No'}")

        return creds
    except Exception as e:
        print(f"\nError completing OAuth flow: {e}")
        print("\nTroubleshooting:")
        print("- Make sure the Google Fit API is enabled in your Google Cloud project")
        print("- Make sure the OAuth client is an installed/desktop app client")
        print("- Restricted fitness scopes may require OAuth consent screen verification")
        return None


if __name__ == "__main__":
    main()
