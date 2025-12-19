# Music MCP Server

A Model Context Protocol (MCP) server that allows controlling music playback through GitHub Copilot Chat.

## Features

- Play/Pause music
- Skip to next/previous track
- Get current track information
- Manage playlists

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up Spotify API credentials:
   - Create a Spotify app at https://developer.spotify.com/dashboard
   - Set environment variables:
     ```bash
     export SPOTIFY_CLIENT_ID=your_client_id
     export SPOTIFY_CLIENT_SECRET=your_client_secret
     export SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
     ```

3. Run the server:
   ```bash
   python server.py
   ```

## Usage

Connect this MCP server to your MCP client (e.g., GitHub Copilot) to control Spotify.