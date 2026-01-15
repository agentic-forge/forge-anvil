# Implementation: Custom Headers Support

**Status: IMPLEMENTED**

## Overview

Add support for custom HTTP headers in forge-anvil to enable compatibility with MCP servers that require headers (e.g., RL Gym MCP servers that need `x-database-id`).

## Problem

RL Gym MCP servers require an `x-database-id` header for tool execution:

```bash
curl -X POST "https://rl-gym-sn-itsm-dev.turing.com/mcp" \
  -H "x-database-id: db_1768494281337_7zla3mzjt" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", ...}'
```

Previously, forge-anvil's `AnvilClient` only passed a URL string to `fastmcp.Client`, which didn't allow specifying custom headers.

## Solution

fastmcp already supports headers at the transport level. The `StreamableHttpTransport` accepts a `headers` parameter:

```python
# In fastmcp/client/transports.py
class StreamableHttpTransport(ClientTransport):
    def __init__(self, url: AnyUrl | str, headers: dict[str, str] | None = None, ...):
        self.headers = headers or {}
```

We exposed this in `AnvilClient`, the CLI, and the Web UI.

## Changes Made

### 1. Updated `AnvilClient` (`src/forge_anvil/client.py`)

```python
from fastmcp import Client
from fastmcp.client.transports import SSETransport, StreamableHttpTransport
from fastmcp.mcp_config import infer_transport_type_from_url

class AnvilClient:
    def __init__(
        self,
        server_url: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.server_url = server_url
        self.timeout = timeout
        self.headers = headers or {}

    def _create_transport(self) -> SSETransport | StreamableHttpTransport:
        """Create transport with headers support."""
        transport_type = infer_transport_type_from_url(self.server_url)
        if transport_type == "sse":
            return SSETransport(url=self.server_url, headers=self.headers)
        else:
            return StreamableHttpTransport(url=self.server_url, headers=self.headers)

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            transport = self._create_transport()
            async with Client(transport) as client:
                result = await client.call_tool(name, arguments or {})
                return {
                    "content": _content_to_list(result),
                    "is_error": getattr(result, "isError", False),
                }
        except Exception as e:
            raise ToolCallError(f"Failed to call tool '{name}': {e}") from e

    # Update all other methods similarly...
```

### 2. Updated CLI (`src/forge_anvil/cli.py`)

Added a `--header` option that can be repeated:

```python
HeaderOption = Annotated[
    list[str] | None,
    typer.Option(
        "--header",
        "-H",
        help="Custom header in 'Key: Value' format (can be repeated)",
    ),
]

def parse_headers(headers: list[str] | None) -> dict[str, str]:
    """Parse header strings into a dictionary."""
    if not headers:
        return {}
    result = {}
    for h in headers:
        if ": " not in h:
            raise typer.BadParameter(f"Invalid header format: '{h}'. Use 'Key: Value' format.")
        key, value = h.split(": ", 1)
        result[key] = value
    return result

@app.command()
def call(
    tool: Annotated[str, typer.Argument(help="Tool name to call")],
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
    # ... other options
) -> None:
    async def _call() -> None:
        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        # ...
```

### 3. Updated Web UI (`src/forge_anvil/ui/index.html`)

Added a collapsible "Custom Headers" section in the UI:

- Header key-value pairs can be added/removed dynamically
- Headers are included in all MCP requests (initialize, notifications, tool calls, etc.)
- UI shows a count badge when headers are configured

Key changes:
- Added `customHeaders` reactive array to store header pairs
- Added `showHeaders` toggle for collapsible section
- Added `addHeader()`, `removeHeader()`, `getCustomHeadersObject()` functions
- Modified `mcpRequest()` function to merge custom headers with request headers

### 4. Usage Examples

CLI usage:

```bash
# Call tool with custom header
anvil call get_user \
  --server https://rl-gym-sn-itsm-dev.turing.com/mcp \
  --header "x-database-id: db_1768494281337_7zla3mzjt" \
  --arg user_id=USER_001

# Multiple headers
anvil call some_tool \
  --header "x-database-id: db_123" \
  --header "x-custom: value"

# Environment variable for common headers (future enhancement)
export ANVIL_HEADERS="x-database-id: db_123"
```

## Testing

### Manual Test with RL Gym

```bash
# Should work after implementation
anvil call get_count_of_incident_priority_wise \
  --server https://rl-gym-sn-itsm-dev.turing.com/mcp \
  --header "x-database-id: db_1768494281337_7zla3mzjt" \
  --json-args '{"priority_list": ["high"]}'
```

### Unit Tests

Add tests in `tests/test_client.py`:

```python
def test_headers_passed_to_transport():
    """Verify headers are passed to the transport."""
    client = AnvilClient("http://example.com/mcp", headers={"x-test": "value"})
    transport = client._create_transport()
    assert transport.headers == {"x-test": "value"}
```

## Files Modified

1. `src/forge_anvil/client.py` - Added headers support to AnvilClient
2. `src/forge_anvil/cli.py` - Added --header CLI option to all commands
3. `src/forge_anvil/ui/index.html` - Added Custom Headers UI section

## Web UI Screenshots

The Web UI now includes a collapsible "Custom Headers" section below the connection bar:

1. Click "Custom Headers" to expand the section
2. Click "+ Add Header" to add a new header row
3. Enter the header name (e.g., `x-database-id`) and value
4. Headers are automatically included in all requests when you connect or call tools
5. A badge shows the count of configured headers
