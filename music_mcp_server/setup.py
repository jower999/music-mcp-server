#!/usr/bin/env python3
"""
Music MCP Server Setup

Run this once to authenticate with Spotify and save your credentials.
After setup, you can use the MCP server without any additional configuration.
"""
import os
import sys
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

def get_config_dir() -> Path:
    """Get the config directory for storing credentials."""
    if sys.platform == "darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "music-mcp-server"
    elif sys.platform == "win32":
        config_dir = Path(os.environ.get("APPDATA", Path.home())) / "music-mcp-server"
    else:
        config_dir = Path.home() / ".config" / "music-mcp-server"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_credentials_path() -> Path:
    """Get path to credentials file."""
    return get_config_dir() / "credentials.json"

def save_credentials(client_id: str, client_secret: str, refresh_token: str, access_token: str, redirect_uri: str):
    """Save credentials to config file."""
    creds = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "access_token": access_token,
        "redirect_uri": redirect_uri,
    }
    with open(get_credentials_path(), "w") as f:
        json.dump(creds, f, indent=2)
    print(f"✅ Credentials saved to {get_credentials_path()}")

def load_credentials() -> dict | None:
    """Load credentials from config file."""
    creds_path = get_credentials_path()
    if creds_path.exists():
        with open(creds_path) as f:
            return json.load(f)
    return None

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback."""
    auth_code = None
    
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if 'code' in query:
            CallbackHandler.auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html><body style="font-family: system-ui; text-align: center; padding: 50px;">
                <h1>Success!</h1>
                <p>You can close this window and return to the terminal.</p>
                </body></html>
            ''')
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Error: No code received</h1>')
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def main():
    """Interactive setup for Music MCP Server."""
    print("=" * 60)
    print("🎵 Music MCP Server Setup")
    print("=" * 60)
    print()
    
    # Check for existing credentials
    existing = load_credentials()
    if existing:
        print(f"Found existing credentials at {get_credentials_path()}")
        response = input("Do you want to reconfigure? [y/N]: ").strip().lower()
        if response != 'y':
            print("Setup cancelled. Your existing credentials are still valid.")
            return
    
    print("To use this MCP server, you need a Spotify Developer account.")
    print()
    print("Step 1: Create a Spotify App")
    print("-" * 40)
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Log in and click 'Create App'")
    print("3. Fill in:")
    print("   - App name: Music MCP Server")
    print("   - App description: Control Spotify from Copilot")
    print("   - Redirect URI: (we'll set this in the next step)")
    print("4. Check 'Web API' and agree to terms")
    print("5. Click 'Save'")
    print()
    
    input("Press Enter when you've created the app...")
    print()
    
    print("Step 2: Get your credentials")
    print("-" * 40)
    print("In your Spotify app settings, find your Client ID and Client Secret.")
    print()
    
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Error: Client ID and Secret are required")
        sys.exit(1)
    
    print()
    print("Step 3: Set your Redirect URI")
    print("-" * 40)
    print("The redirect URI is where Spotify sends you after login.")
    print("Options:")
    print("  - http://localhost:8888/callback (default, for local use)")
    print("  - https://your-ngrok-url.ngrok-free.app/callback (for remote/HTTPS)")
    print()
    redirect_uri = input("Enter your Redirect URI [http://localhost:8888/callback]: ").strip()
    if not redirect_uri:
        redirect_uri = "http://localhost:8888/callback"
    
    # Parse the redirect URI to get host and port for the local server
    from urllib.parse import urlparse
    parsed = urlparse(redirect_uri)
    callback_host = parsed.hostname or "localhost"
    callback_port = parsed.port or 8888
    
    print()
    print(f"⚠️  Make sure this Redirect URI is added to your Spotify app settings!")
    print(f"   URI: {redirect_uri}")
    input("Press Enter when you've added it...")
    
    print()
    print("Step 4: Authorize the app")
    print("-" * 40)
    
    # Build auth URL
    scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-modify-public,playlist-modify-private,playlist-read-private"
    
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )
    
    # Start local server to catch the callback
    # Only start if using localhost
    if callback_host in ("localhost", "127.0.0.1"):
        print(f"Starting local server on port {callback_port} for OAuth callback...")
        server = HTTPServer(('localhost', callback_port), CallbackHandler)
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        print("Opening browser for Spotify authorization...")
        print(f"If browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)
        
        # Wait for callback
        server_thread.join(timeout=120)
        server.server_close()
        
        if not CallbackHandler.auth_code:
            print("❌ Error: No authorization code received. Please try again.")
            sys.exit(1)
    else:
        # For non-localhost (e.g., ngrok), we need to ask for the code manually
        print()
        print("Since you're using a non-localhost redirect URI, you'll need to")
        print("copy the authorization code from the callback URL.")
        print()
        print(f"1. Open this URL in your browser:")
        print(f"   {auth_url}")
        print()
        print("2. After authorizing, you'll be redirected to your callback URL.")
        print("3. Copy the 'code' parameter from the URL.")
        print("   Example: ...callback?code=AQB...xyz")
        print()
        webbrowser.open(auth_url)
        CallbackHandler.auth_code = input("Enter the authorization code: ").strip()
        
        if not CallbackHandler.auth_code:
            print("❌ Error: No authorization code provided. Please try again.")
            sys.exit(1)
    
    # Exchange code for tokens
    print("Exchanging code for tokens...")
    import base64
    import urllib.request
    import urllib.parse
    
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': CallbackHandler.auth_code,
        'redirect_uri': redirect_uri,
    }).encode()
    
    req = urllib.request.Request(
        'https://accounts.spotify.com/api/token',
        data=data,
        headers={
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            token_data = json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Error getting tokens: {e}")
        sys.exit(1)
    
    # Save credentials
    save_credentials(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=token_data['refresh_token'],
        access_token=token_data['access_token'],
        redirect_uri=redirect_uri,
    )
    
    print()
    print("=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print()
    print("You can now use the MCP server with GitHub Copilot.")
    print()
    print("Add this to your MCP settings:")
    print()
    print(json.dumps({
        "mcpServers": {
            "music": {
                "command": "music-mcp-server"
            }
        }
    }, indent=2))
    print()

if __name__ == "__main__":
    main()
