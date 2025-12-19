# GitHub Copilot Instructions for Music MCP Server

This is an MCP (Model Context Protocol) server that allows controlling music playback through GitHub Copilot Chat. It integrates with Spotify's API to provide music control functionality.

## Development Guidelines

- **Python Version**: Use Python 3.12 for development and deployment.
- **Virtual Environment**: Always use a virtual environment when running or developing this project.
  - Create: `python3.12 -m venv venv`
  - Activate: `source venv/bin/activate` (on macOS/Linux)
  - Install dependencies: `pip install -r requirements.txt`
- **Environment Variables**: Use a `.env` file for sensitive data like Spotify API credentials. Never commit actual credentials.
- **Code Style**: Follow PEP 8 standards. Use type hints where possible.
- **Testing**: Test all changes locally before committing. Ensure the MCP server can start without errors.

## Project Structure

- `server.py`: Main MCP server implementation with Spotify integration tools.
- `requirements.txt`: Python dependencies.
- `.env`: Environment variables (not committed).
- `.gitignore`: Excludes sensitive files and cache.

## Setup Steps

1. Ensure Python 3.12 is installed.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Set up Spotify API credentials in `.env` file.
5. Run the server: `python server.py`

## Common Tasks

- Adding new music control features: Implement as new MCP tools in `server.py`.
- Updating dependencies: Update `requirements.txt` and test compatibility.
- Debugging: Check Spotify API responses and MCP protocol compliance.