import asyncio
import os
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import mcp.server.stdio
from mcp import Tool
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# Spotify setup
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope='user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-modify-public,playlist-modify-private,playlist-read-private'
))

server = Server("spotify-mcp-server")

@server.tool()
async def play_music() -> str:
    """Play or resume music on Spotify."""
    try:
        sp.start_playback()
        return "Music started playing."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def pause_music() -> str:
    """Pause music on Spotify."""
    try:
        sp.pause_playback()
        return "Music paused."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def next_track() -> str:
    """Skip to the next track."""
    try:
        sp.next_track()
        return "Skipped to next track."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def previous_track() -> str:
    """Go to the previous track."""
    try:
        sp.previous_track()
        return "Went to previous track."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def current_track() -> str:
    """Get information about the currently playing track."""
    try:
        current = sp.currently_playing()
        if current and current['item']:
            track = current['item']
            return f"Now playing: {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}"
        else:
            return "No track is currently playing."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_devices() -> str:
    """Get list of available Spotify devices."""
    try:
        devices = sp.devices()
        device_info = []
        for device in devices['devices']:
            status = "Active" if device['is_active'] else "Inactive"
            device_info.append(f"{device['name']} (ID: {device['id']}, Type: {device['type']}, {status})")
        return "Available devices:\n" + "\n".join(device_info)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def transfer_playback(device_id: str) -> str:
    """Transfer playback to a specific device."""
    try:
        sp.transfer_playback(device_id)
        return f"Transferred playback to device."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_playlists() -> str:
    """Get user's playlists."""
    try:
        playlists = sp.current_user_playlists()
        playlist_info = []
        for pl in playlists['items']:
            playlist_info.append(f"{pl['name']} (ID: {pl['id']})")
        return "Your playlists:\n" + "\n".join(playlist_info)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def create_playlist(name: str, description: str = "", public: bool = True) -> str:
    """Create a new playlist."""
    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, name, public=public, description=description)
        return f"Created playlist '{name}' with ID: {playlist['id']}"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def add_to_playlist(playlist_id: str, track_uri: str) -> str:
    """Add a track to a playlist by URI."""
    try:
        sp.playlist_add_items(playlist_id, [track_uri])
        return f"Added track to playlist."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def remove_from_playlist(playlist_id: str, track_uri: str) -> str:
    """Remove a track from a playlist by URI."""
    try:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
        return f"Removed track from playlist."
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_playlist_tracks(playlist_id: str) -> str:
    """Get tracks in a playlist."""
    try:
        results = sp.playlist_tracks(playlist_id)
        tracks = []
        for item in results['items']:
            track = item['track']
            tracks.append(f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])} (URI: {track['uri']})")
        return "Tracks in playlist:\n" + "\n".join(tracks)
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def delete_playlist(playlist_id: str) -> str:
    """Delete (unfollow) a playlist."""
    try:
        user_id = sp.current_user()['id']
        sp.user_playlist_unfollow(user_id, playlist_id)
        return f"Deleted playlist."
    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())