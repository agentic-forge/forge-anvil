"""Tests for AnvilClient."""

import pytest

from forge_anvil.client import AnvilClient, AnvilError, ConnectionError, ToolCallError


class TestAnvilClientInit:
    """Tests for AnvilClient initialization."""

    def test_init_with_url(self) -> None:
        """Test client initialization with URL."""
        client = AnvilClient("http://localhost:8000/mcp")
        assert client.server_url == "http://localhost:8000/mcp"
        assert client.timeout == 30.0

    def test_init_with_custom_timeout(self) -> None:
        """Test client initialization with custom timeout."""
        client = AnvilClient("http://localhost:8000/mcp", timeout=60.0)
        assert client.timeout == 60.0


class TestAnvilErrors:
    """Tests for Anvil error classes."""

    def test_anvil_error_is_base(self) -> None:
        """Test that AnvilError is the base exception."""
        assert issubclass(ConnectionError, AnvilError)
        assert issubclass(ToolCallError, AnvilError)

    def test_connection_error_message(self) -> None:
        """Test ConnectionError message."""
        error = ConnectionError("Failed to connect")
        assert str(error) == "Failed to connect"

    def test_tool_call_error_message(self) -> None:
        """Test ToolCallError message."""
        error = ToolCallError("Tool not found")
        assert str(error) == "Tool not found"


class TestAnvilClientConnectionError:
    """Tests for connection errors."""

    @pytest.mark.asyncio
    async def test_list_tools_connection_error(self) -> None:
        """Test that list_tools raises ConnectionError on failure."""
        client = AnvilClient("http://invalid-server:9999/mcp")
        with pytest.raises(ConnectionError):
            await client.list_tools()

    @pytest.mark.asyncio
    async def test_ping_returns_false_on_connection_error(self) -> None:
        """Test that ping returns False on connection error."""
        client = AnvilClient("http://invalid-server:9999/mcp")
        result = await client.ping()
        assert result is False
