#!/usr/bin/env python3
"""
Google Fit OAuth Authorization Script (Device Flow)
For headless environments where user can't easily paste redirect URLs.
Uses device flow or manual code exchange.
"""

import os
import json
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes needed for fitness data (read-only)
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
]

CREDENTIALS_FILE = 'credentials/google-fit-credentials.json'
TOKEN_FILE = 'credentials/google-fit-token.json'


def main():
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        print(f"Loading existing token from {TOKEN_FILE}")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if creds and creds.valid:
        print("✅ Token already valid! Ready to use.")
        return creds
    
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing expired token...")
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print("✅ Token refreshed!")
        return creds
    
    # Need new OAuth flow
    print("Starting OAuth flow...")
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found!")
        return
    
    # Read credentials
    with open(CREDENTIALS_FILE, 'r') as f:
        creds_data = json.load(f)
    
    # Use installed app flow with manual redirect
    client_config = creds_data
    
    # Create flow with explicit redirect URI
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Manual copy-paste redirect
    )
    
    # Generate auth URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("\n" + "="*60)
    print("🔐 GOOGLE FIT AUTHORIZATION REQUIRED")
    print("="*60)
    print("\n1. Visit this URL in your browser:")
    print(f"\n{auth_url}\n")
    print("2. Sign in with: josuelruiz2127@gmail.com")
    print("3. Grant permission for fitness data access")
    print("4. Google will show you an AUTHORIZATION CODE")
    print("5. Copy that code and paste it below:\n")
    
    auth_code = input("Paste authorization code: ").strip()
    
    if not auth_code:
        print("❌ No code provided. Exiting.")
        return
    
    print(f"\n✅ Got authorization code: {auth_code[:20]}...")
    
    # Exchange code for token
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Token saved to {TOKEN_FILE}")
        print(f"✅ Ready to access Google Fit API!")
        print(f"Token expires: {creds.expiry}")
        print(f"Refresh token: {'✅ Yes' if creds.refresh_token else '❌ No'}")
        
        return creds
    except Exception as e:
        print(f"\n❌ Error exchanging code: {e}")
        print("\nTroubleshooting:")
        print("- Make sure you copied the FULL code (not the URL)")
        print("- The code may have expired (valid for ~10 minutes)")
        print("- Try generating a new code by visiting the URL again")
        return


if __name__ == '__main__':
    main()
