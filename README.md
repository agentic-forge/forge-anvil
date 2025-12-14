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
