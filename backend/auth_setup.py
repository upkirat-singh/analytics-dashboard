"""
auth_setup.py – Run this ONCE from the command line to authorize the dashboard.

Usage:
    python auth_setup.py

What it does:
  1. Opens a browser window to Google's consent screen.
  2. After you click "Allow", saves the token to token.json in this folder.
  3. The Flask app (app.py) will pick up token.json automatically on next start.

Scopes requested: Google Analytics (read-only) + Search Console (read-only).
Re-run this script whenever scopes change or you need to re-authorize.
"""

import os
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: google-auth-oauthlib is not installed.")
    print("Run:  pip install google-auth-oauthlib")
    sys.exit(1)

# Paths (relative to this script's location)
BASE_DIR = Path(__file__).parent
CLIENT_SECRETS = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

def main():
    if not CLIENT_SECRETS.exists():
        print(f"ERROR: client_secret.json not found at {CLIENT_SECRETS}")
        print("Download a 'Desktop app' type OAuth client from:")
        print("  https://console.cloud.google.com/apis/credentials")
        sys.exit(1)

    print("Opening browser for Google OAuth consent...")
    print("(If the browser doesn't open automatically, check the URL printed below.)\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), scopes=SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"\n✅ Done! Token saved to: {TOKEN_FILE}")
    print("You can now start the Flask server with:  python app.py")

if __name__ == "__main__":
    main()
