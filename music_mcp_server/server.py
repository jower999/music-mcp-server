#!/usr/bin/env python3
"""
Music MCP Server

Control Spotify playback from GitHub Copilot Chat via MCP.
"""
import os
import sys
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_config_dir() -> Path:
    """Get the config directory for storing credentials."""
    if sys.platform == "darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "music-mcp-server"
    elif sys.platform == "win32":
        config_dir = Path(os.environ.get("APPDATA", Path.home())) / "music-mcp-server"
    else:
        config_dir = Path.home() / ".config" / "music-mcp-server"
    return config_dir

def get_credentials_path() -> Path:
    """Get path to credentials file."""
    return get_config_dir() / "credentials.json"

def load_credentials() -> dict | None:
    """Load credentials from config file."""
    creds_path = get_credentials_path()
    if creds_path.exists():
        with open(creds_path) as f:
            return json.load(f)
    return None

def get_spotify_client() -> spotipy.Spotify:
    """Get authenticated Spotify client."""
    creds = load_credentials()
    
    if not creds:
        print("❌ No credentials found. Please run 'music-mcp-setup' first.", file=sys.stderr)
        sys.exit(1)
    
    # Create a cache handler that uses our stored credentials
    cache_path = get_config_dir() / ".spotify_cache"
    
    # Write spotipy-compatible cache
    cache_data = {
        "access_token": creds["access_token"],
        "refresh_token": creds["refresh_token"],
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-modify-public playlist-modify-private playlist-read-private",
        "expires_at": 0,  # Force refresh on first use
    }
    with open(cache_path, "w") as f:
        json.dump(cache_data, f)
    
    auth_manager = SpotifyOAuth(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        redirect_uri="http://localhost:8888/callback",
        scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-modify-public,playlist-modify-private,playlist-read-private",
        cache_path=str(cache_path),
    )
    
    return spotipy.Spotify(auth_manager=auth_manager)

# Initialize Spotify client
sp = get_spotify_client()

# Initialize MCP server
app = FastMCP("music-mcp-server")

# =============================================================================
# Playback Controls
# =============================================================================

@app.tool()
async def play_music() -> str:
    """Play or resume music on Spotify."""
    try:
        sp.start_playback()
        return "▶️ Music started playing."
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def pause_music() -> str:
    """Pause music on Spotify."""
    try:
        sp.pause_playback()
        return "⏸️ Music paused."
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def next_track() -> str:
    """Skip to the next track."""
    try:
        sp.next_track()
        return "⏭️ Skipped to next track."
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def previous_track() -> str:
    """Go to the previous track."""
    try:
        sp.previous_track()
        return "⏮️ Went to previous track."
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def current_track() -> str:
    """Get information about the currently playing track."""
    try:
        current = sp.currently_playing()
        if current and current['item']:
            track = current['item']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            return f"🎵 Now playing: {track['name']} by {artists}"
        else:
            return "No track is currently playing."
    except Exception as e:
        return f"Error: {str(e)}"

# =============================================================================
# Device Management
# =============================================================================

@app.tool()
async def get_devices() -> str:
    """Get list of available Spotify devices."""
    try:
        devices = sp.devices()
        if not devices['devices']:
            return "No devices found. Make sure Spotify is open on at least one device."
        device_info = []
        for device in devices['devices']:
            status = "🟢 Active" if device['is_active'] else "⚪ Inactive"
            device_info.append(f"{device['name']} ({device['type']}) - {status}\n  ID: {device['id']}")
        return "Available devices:\n" + "\n".join(device_info)
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def transfer_playback(device_id: str) -> str:
    """Transfer playback to a specific device by its ID."""
    try:
        sp.transfer_playback(device_id)
        return f"🔄 Transferred playback to device."
    except Exception as e:
        return f"Error: {str(e)}"

# =============================================================================
# Playlist Management
# =============================================================================

@app.tool()
async def get_playlists() -> str:
    """Get your Spotify playlists."""
    try:
        playlists = sp.current_user_playlists()
        if not playlists['items']:
            return "No playlists found."
        playlist_info = []
        for pl in playlists['items']:
            playlist_info.append(f"📋 {pl['name']}\n  ID: {pl['id']}")
        return "Your playlists:\n" + "\n".join(playlist_info)
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def create_playlist(name: str, description: str = "", public: bool = True) -> str:
    """Create a new playlist."""
    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, name, public=public, description=description)
        return f"✅ Created playlist '{name}'\n  ID: {playlist['id']}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def add_to_playlist(playlist_id: str, track_uri: str) -> str:
    """Add a track to a playlist. Track URI format: spotify:track:XXXXXX"""
    try:
        sp.playlist_add_items(playlist_id, [track_uri])
        return f"✅ Added track to playlist."
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def remove_from_playlist(playlist_id: str, track_uri: str) -> str:
    """Remove a track from a playlist. Track URI format: spotify:track:XXXXXX"""
    try:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
        return f"✅ Removed track from playlist."
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def get_playlist_tracks(playlist_id: str) -> str:
    """Get tracks in a playlist."""
    try:
        results = sp.playlist_tracks(playlist_id)
        if not results['items']:
            return "Playlist is empty."
        tracks = []
        for item in results['items']:
            track = item['track']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            tracks.append(f"🎵 {track['name']} - {artists}\n  URI: {track['uri']}")
        return "Tracks in playlist:\n" + "\n".join(tracks)
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def delete_playlist(playlist_id: str) -> str:
    """Delete (unfollow) a playlist."""
    try:
        user_id = sp.current_user()['id']
        sp.user_playlist_unfollow(user_id, playlist_id)
        return f"🗑️ Deleted playlist."
    except Exception as e:
        return f"Error: {str(e)}"

# =============================================================================
# Search
# =============================================================================

@app.tool()
async def search_tracks(query: str, limit: int = 5) -> str:
    """Search for tracks on Spotify."""
    try:
        results = sp.search(q=query, type='track', limit=limit)
        if not results['tracks']['items']:
            return f"No tracks found for '{query}'."
        tracks = []
        for track in results['tracks']['items']:
            artists = ', '.join([artist['name'] for artist in track['artists']])
            tracks.append(f"🎵 {track['name']} - {artists}\n  URI: {track['uri']}")
        return f"Search results for '{query}':\n" + "\n".join(tracks)
    except Exception as e:
        return f"Error: {str(e)}"

@app.tool()
async def play_track(track_uri: str) -> str:
    """Play a specific track by URI. Format: spotify:track:XXXXXX"""
    try:
        sp.start_playback(uris=[track_uri])
        return f"▶️ Playing track."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Run the MCP server."""
    app.run()

if __name__ == "__main__":
    main()
