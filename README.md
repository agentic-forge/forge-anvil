# Forge Anvil

MCP client tool for testing MCP servers.

## Features

- **CLI Interface** - Test MCP servers from the command line
- **Web UI** - Interactive browser-based inspector
- **No build step** - Web UI is a single HTML file with Vue.js

## Installation

```bash
# Clone the repository
git clone https://github.com/agentic-forge/forge-anvil.git
cd forge-anvil

# Install dependencies
uv sync
```

## CLI Usage

```bash
# Show server info
anvil info --server http://localhost:8000/mcp

# List available tools
anvil list-tools

# Call a tool
anvil call get_current_weather --arg city=Berlin

# Call with JSON arguments
anvil call get_forecast --json-args '{"city": "Tokyo", "days": 3}'

# Output as JSON
anvil list-tools --json

# List resources and prompts
anvil list-resources
anvil list-prompts
```

### Environment Variable

Set `ANVIL_SERVER` to avoid passing `--server` every time:

```bash
export ANVIL_SERVER=http://localhost:8000/mcp
anvil list-tools
```

## Web UI

Launch the interactive inspector:

```bash
anvil ui --port 5000
```

Open http://localhost:5000 in your browser.

## Using with Forge MCP Servers

Anvil is designed to work with any MCP server, but integrates seamlessly with Forge MCP servers built with FastMCP.

### Example: Testing mcp-weather

**Terminal 1 - Start the MCP server:**

```bash
cd /path/to/agentic-forge/mcp-servers/mcp-weather
uv sync
uv run python -m forge_mcp_weather
# Server starts at http://localhost:8000/mcp
```

**Terminal 2 - Use Anvil to test:**

```bash
cd /path/to/agentic-forge/forge-anvil

# Set the server URL (optional, this is the default)
export ANVIL_SERVER=http://localhost:8000/mcp

# Check server info
anvil info

# List available tools
anvil list-tools

# Get current weather
anvil call get_current_weather --arg city=Berlin

# Get weather with imperial units
anvil call get_current_weather --arg city="New York" --arg units=imperial

# Get 5-day forecast
anvil call get_forecast --json-args '{"city": "Tokyo", "days": 5}'

# Get air quality
anvil call get_air_quality --arg city=Beijing

# Geocode a city
anvil call geocode --arg city=London --arg country=UK
```

### Using the Web UI with Forge Servers

```bash
# Start the MCP server (Terminal 1)
cd /path/to/mcp-weather
uv run python -m forge_mcp_weather

# Launch Anvil UI (Terminal 2)
cd /path/to/forge-anvil
anvil ui

# Browser opens automatically at http://localhost:5000
# The UI connects to http://localhost:8000/mcp by default
```

### Other Forge MCP Servers

Anvil works with any Forge MCP server following the same pattern:

```bash
# Start any Forge MCP server
uv run python -m forge_mcp_<server_name>

# Test with Anvil
anvil list-tools --server http://localhost:8000/mcp
```

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Type checking
uv run basedpyright

# Linting
uv run ruff check .

# Install pre-commit hooks
uv run pre-commit install
```

## License

MIT
