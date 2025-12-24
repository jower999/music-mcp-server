# uv: Fast Python Package Management

## What is uv?

`uv` is a fast Python package installer and resolver written in Rust. It's designed as a drop-in replacement for `pip` and `pip-tools` that offers significant performance improvements.

## Key Features

### 🚀 Blazing Fast
- **10-100x faster** than pip for most operations
- Written in Rust for optimal performance
- Parallel dependency resolution

### 📦 Drop-in Replacement
- Compatible with existing `requirements.txt` files
- Same command-line interface as pip
- Works with virtual environments

### 🛡️ Secure
- Built-in dependency auditing
- Automatic hash checking
- Reproducible builds

## Basic Usage

```bash
# Install packages
uv pip install requests fastapi

# Install from requirements.txt
uv pip install -r requirements.txt

# Create virtual environment
uv venv myenv

# Run Python scripts with dependencies
uv run python script.py

# Add dependencies to project
uv add requests
```

## Why Use uv?

1. **Speed**: Install packages in seconds instead of minutes
2. **Reliability**: Better dependency resolution avoids conflicts
3. **Modern**: Built with contemporary Python packaging best practices
4. **Ecosystem**: Integrates with tools like ruff, mypy, and pytest

## Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

## Common Commands

| Command | Description |
|---------|-------------|
| `uv pip install <package>` | Install packages |
| `uv pip install -r requirements.txt` | Install from requirements file |
| `uv venv <name>` | Create virtual environment |
| `uv run <command>` | Run command with project dependencies |
| `uv add <package>` | Add dependency to project |
| `uv remove <package>` | Remove dependency from project |

## Integration with Our Project

In our music MCP server project, uv can be used to:
- Quickly install dependencies: `uv pip install -r requirements.txt`
- Create isolated environments: `uv venv venv`
- Run the server: `uv run python server.py`

uv is particularly useful for Python projects that need fast, reliable dependency management.