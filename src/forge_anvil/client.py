"""MCP client wrapper for Anvil."""

from __future__ import annotations

from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class AnvilError(Exception):
    """Base exception for Anvil errors."""


class ConnectionError(AnvilError):
    """Failed to connect to MCP server."""


class ToolCallError(AnvilError):
    """Failed to call a tool."""


class AnvilClient:
    """Wrapper around fastmcp.Client for CLI/UI usage.

    Provides a simpler interface that returns plain dictionaries
    instead of MCP types, making it easier to serialize to JSON.
    """

    def __init__(
        self,
        server_url: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            server_url: URL of the MCP server (e.g., http://localhost:8000/mcp)
            timeout: Request timeout in seconds
            headers: Custom HTTP headers to send with requests
        """
        self.server_url = server_url
        self.timeout = timeout
        self.headers = headers or {}

    def _create_transport(self) -> StreamableHttpTransport:
        """Create transport with headers support."""
        return StreamableHttpTransport(url=self.server_url, headers=self.headers)

    def _create_client(self) -> Client:
        """Create a Client instance with headers if specified."""
        if self.headers:
            return Client(self._create_transport())
        return Client(self.server_url)

    async def get_server_info(self) -> dict[str, Any]:
        """Get server capabilities and info.

        Returns:
            Dictionary with server info:
            - name: Server name
            - version: Server version
            - protocol_version: MCP protocol version
            - capabilities: Server capabilities
            - instructions: Server instructions (if provided)
        """
        try:
            async with self._create_client() as client:
                # Get server info from initialize_result (set after connection)
                init_result = client.initialize_result

                if init_result is not None:
                    info = getattr(init_result, "serverInfo", None)
                    name = getattr(info, "name", "Unknown") if info else "Unknown"
                    version = getattr(info, "version", "Unknown") if info else "Unknown"
                    return {
                        "name": name,
                        "version": version,
                        "protocol_version": getattr(init_result, "protocolVersion", "Unknown"),
                        "capabilities": _capabilities_to_dict(
                            getattr(init_result, "capabilities", None)
                        ),
                        "instructions": getattr(init_result, "instructions", None),
                    }

                return {
                    "name": "Unknown",
                    "version": "Unknown",
                    "protocol_version": "Unknown",
                    "capabilities": {},
                    "instructions": None,
                }
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.server_url}: {e}") from e

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from the server.

        Returns:
            List of tools with name, description, and input_schema.
        """
        try:
            async with self._create_client() as client:
                tools = await client.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                    for tool in tools
                ]
        except Exception as e:
            raise ConnectionError(f"Failed to list tools: {e}") from e

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call a tool and return the result.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Dictionary with content and is_error flag.
        """
        try:
            async with self._create_client() as client:
                result = await client.call_tool(name, arguments or {})
                return {
                    "content": _content_to_list(result),
                    "is_error": getattr(result, "isError", False),
                }
        except Exception as e:
            raise ToolCallError(f"Failed to call tool '{name}': {e}") from e

    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources from the server.

        Returns:
            List of resources with uri, name, description, and mime_type.
        """
        try:
            async with self._create_client() as client:
                resources = await client.list_resources()
                return [
                    {
                        "uri": str(resource.uri),
                        "name": resource.name,
                        "description": resource.description,
                        "mime_type": resource.mimeType,
                    }
                    for resource in resources
                ]
        except Exception as e:
            raise ConnectionError(f"Failed to list resources: {e}") from e

    async def list_prompts(self) -> list[dict[str, Any]]:
        """List available prompts from the server.

        Returns:
            List of prompts with name, description, and arguments.
        """
        try:
            async with self._create_client() as client:
                prompts = await client.list_prompts()
                return [
                    {
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": [
                            {
                                "name": arg.name,
                                "description": arg.description,
                                "required": arg.required,
                            }
                            for arg in (prompt.arguments or [])
                        ],
                    }
                    for prompt in prompts
                ]
        except Exception as e:
            raise ConnectionError(f"Failed to list prompts: {e}") from e

    async def ping(self) -> bool:
        """Check if server is responsive.

        Returns:
            True if server responds, False otherwise.
        """
        try:
            async with self._create_client() as client:
                await client.ping()
                return True
        except Exception:
            return False


def _capabilities_to_dict(capabilities: Any) -> dict[str, Any]:
    """Convert server capabilities to a dictionary."""
    if capabilities is None:
        return {}

    result: dict[str, Any] = {}

    # Check for common capability attributes
    if hasattr(capabilities, "tools") and capabilities.tools:
        result["tools"] = True
    if hasattr(capabilities, "resources") and capabilities.resources:
        result["resources"] = True
    if hasattr(capabilities, "prompts") and capabilities.prompts:
        result["prompts"] = True
    if hasattr(capabilities, "logging") and capabilities.logging:
        result["logging"] = True

    return result


def _content_to_list(result: Any) -> list[dict[str, Any]]:
    """Convert tool result content to a list of dictionaries."""
    content_list = []

    # Handle different result types
    if hasattr(result, "content"):
        items = result.content if isinstance(result.content, list) else [result.content]
    elif isinstance(result, list):
        items = result
    else:
        items = [result]

    for item in items:
        if hasattr(item, "text"):
            content_list.append({"type": "text", "text": item.text})
        elif hasattr(item, "data"):
            content_list.append(
                {
                    "type": "image",
                    "data": item.data,
                    "mime_type": getattr(item, "mimeType", "image/png"),
                }
            )
        elif isinstance(item, str):
            content_list.append({"type": "text", "text": item})
        elif isinstance(item, dict):
            content_list.append(item)
        else:
            content_list.append({"type": "text", "text": str(item)})

    return content_list
