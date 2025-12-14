"""Tests for Anvil CLI."""

from typer.testing import CliRunner

from forge_anvil.cli import app

runner = CliRunner()


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_main_help(self) -> None:
        """Test main help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "MCP client tool for testing MCP servers" in result.output

    def test_info_help(self) -> None:
        """Test info command help."""
        result = runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "Show server info and capabilities" in result.output

    def test_list_tools_help(self) -> None:
        """Test list-tools command help."""
        result = runner.invoke(app, ["list-tools", "--help"])
        assert result.exit_code == 0
        assert "List available tools from the server" in result.output

    def test_call_help(self) -> None:
        """Test call command help."""
        result = runner.invoke(app, ["call", "--help"])
        assert result.exit_code == 0
        assert "Call a tool with arguments" in result.output

    def test_list_resources_help(self) -> None:
        """Test list-resources command help."""
        result = runner.invoke(app, ["list-resources", "--help"])
        assert result.exit_code == 0
        assert "List available resources from the server" in result.output

    def test_list_prompts_help(self) -> None:
        """Test list-prompts command help."""
        result = runner.invoke(app, ["list-prompts", "--help"])
        assert result.exit_code == 0
        assert "List available prompts from the server" in result.output

    def test_ping_help(self) -> None:
        """Test ping command help."""
        result = runner.invoke(app, ["ping", "--help"])
        assert result.exit_code == 0
        assert "Check if server is responsive" in result.output

    def test_ui_help(self) -> None:
        """Test ui command help."""
        result = runner.invoke(app, ["ui", "--help"])
        assert result.exit_code == 0
        assert "Launch interactive web UI" in result.output


class TestCLIConnectionErrors:
    """Tests for CLI connection error handling."""

    def test_info_connection_error(self) -> None:
        """Test info command handles connection errors."""
        result = runner.invoke(app, ["info", "--server", "http://invalid:9999/mcp"])
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_list_tools_connection_error(self) -> None:
        """Test list-tools command handles connection errors."""
        result = runner.invoke(app, ["list-tools", "--server", "http://invalid:9999/mcp"])
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_ping_connection_error(self) -> None:
        """Test ping command handles connection errors."""
        result = runner.invoke(app, ["ping", "--server", "http://invalid:9999/mcp"])
        assert result.exit_code == 1
        assert "not responding" in result.output
