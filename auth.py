#!/usr/bin/env python3
"""
Run this script first to authenticate with Spotify.
It will cache the token so the MCP server can use it.
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = parse_qs(urlparse(self.path).query)
        if 'code' in query:
            auth_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Success! You can close this window.</h1>')
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

# Create OAuth manager
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope='user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-modify-public,playlist-modify-private,playlist-read-private'
)

# Check if we already have a valid token
token_info = sp_oauth.get_cached_token()
if token_info:
    print("✅ Already authenticated (token cached)")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user = sp.current_user()
    print(f"✅ Logged in as: {user['display_name']}")
    print("\nYou can now run the MCP server!")
else:
    print("Starting auth server on port 8888...")
    print("Make sure ngrok is running: ngrok http 8888")
    print()
    
    # Start local server
    server = HTTPServer(('localhost', 8888), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.start()
    
    # Open browser for auth
    auth_url = sp_oauth.get_authorize_url()
    print(f"Opening browser for Spotify login...")
    print(f"If browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)
    
    # Wait for callback
    server_thread.join(timeout=120)
    server.server_close()
    
    if auth_code:
        # Exchange code for token
        token_info = sp_oauth.get_access_token(auth_code)
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user = sp.current_user()
        print(f"\n✅ Authenticated as: {user['display_name']}")
        print("✅ Token cached in .cache file")
        print("\nYou can now run the MCP server!")
    else:
        print("\n❌ Authentication failed or timed out")
