# Music MCP Server 🎵

Control Spotify playback directly from GitHub Copilot Chat using the Model Context Protocol (MCP).

## Features

- ▶️ **Playback Controls**: Play, pause, skip, previous track
- 🎵 **Now Playing**: See what's currently playing
- 📋 **Playlist Management**: Create, edit, and manage playlists
- 🔄 **Device Control**: Transfer playback between devices
- 🔍 **Search**: Find and play tracks

## Installation

```bash
pip install music-mcp-server
```

## Quick Start

### 1. Run Setup (one-time)

```bash
music-mcp-setup
```

This will guide you through:
1. Creating a Spotify Developer app
2. Authorizing the MCP server
3. Saving your credentials securely

### 2. Add to Your MCP Client

Add this to your MCP settings (e.g., `~/.config/github-copilot/mcp.json`):

```json
{
  "mcpServers": {
    "music": {
      "command": "music-mcp-server"
    }
  }
}
```

### 3. Use with Copilot Chat

Now you can control Spotify from Copilot Chat:
- "What's currently playing?"
- "Play the next track"
- "Search for songs by Taylor Swift"
- "Create a playlist called 'Coding Vibes'"

## Available Commands

| Command | Description |
|---------|-------------|
| `play_music` | Resume playback |
| `pause_music` | Pause playback |
| `next_track` | Skip to next track |
| `previous_track` | Go to previous track |
| `current_track` | Show now playing |
| `search_tracks` | Search for songs |
| `play_track` | Play a specific track |
| `get_devices` | List available devices |
| `transfer_playback` | Switch playback device |
| `get_playlists` | List your playlists |
| `create_playlist` | Create new playlist |
| `add_to_playlist` | Add track to playlist |
| `remove_from_playlist` | Remove track from playlist |
| `get_playlist_tracks` | View playlist tracks |
| `delete_playlist` | Delete a playlist |

## Requirements

- Python 3.10+
- Spotify Premium account (required for playback control)
- Spotify Developer account (free)

## Troubleshooting

### "No credentials found"
Run `music-mcp-setup` to configure your Spotify credentials.

### "No devices found"
Make sure Spotify is open and playing on at least one device.

### "Premium required"
Playback control features require Spotify Premium.

## Development

```bash
# Clone the repo
git clone https://github.com/jower999/music-mcp-server.git
cd music-mcp-server

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Run setup
music-mcp-setup

# Test with MCP Inspector
mcp dev music_mcp_server/server.py
```

## License

MIT