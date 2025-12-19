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
    scope='user-read-playback-state,user-modify-playback-state,user-read-currently-playing'
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
async def get_playlists() -> str:
    """Get user's playlists."""
    try:
        playlists = sp.current_user_playlists()
        playlist_names = [pl['name'] for pl in playlists['items']]
        return "Your playlists: " + ", ".join(playlist_names)
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