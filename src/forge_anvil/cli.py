"""Typer CLI application for Anvil."""

from __future__ import annotations

import warnings

# Suppress deprecation warning from upstream MCP SDK about streamable_http_client
# See: https://github.com/jlowin/fastmcp/issues/XXX (tracked upstream)
warnings.filterwarnings(
    "ignore",
    message="Use `streamable_http_client` instead.",
    category=DeprecationWarning,
)

import asyncio  # noqa: E402
import json  # noqa: E402
from typing import Annotated  # noqa: E402

import typer  # noqa: E402

from forge_anvil.client import AnvilClient, AnvilError  # noqa: E402
from forge_anvil.output import (  # noqa: E402
    console,
    print_error,
    print_info,
    print_prompts,
    print_resources,
    print_result,
    print_tool_detail,
    print_tools,
)

app = typer.Typer(
    name="anvil",
    help="MCP client tool for testing MCP servers.",
    no_args_is_help=True,
)

# Global options
ServerOption = Annotated[
    str,
    typer.Option(
        "--server",
        "-s",
        help="MCP server URL",
        envvar="ANVIL_SERVER",
    ),
]

HeaderOption = Annotated[
    list[str] | None,
    typer.Option(
        "--header",
        "-H",
        help="Custom header in 'Key: Value' format (can be repeated)",
    ),
]

JsonOption = Annotated[
    bool,
    typer.Option(
        "--json",
        "-j",
        help="Output as JSON",
    ),
]


def parse_headers(headers: list[str] | None) -> dict[str, str]:
    """Parse header strings into a dictionary.

    Args:
        headers: List of headers in 'Key: Value' format

    Returns:
        Dictionary of header names to values

    Raises:
        typer.BadParameter: If a header is not in 'Key: Value' format
    """
    if not headers:
        return {}
    result = {}
    for h in headers:
        if ": " not in h:
            raise typer.BadParameter(f"Invalid header format: '{h}'. Use 'Key: Value' format.")
        key, value = h.split(": ", 1)
        result[key] = value
    return result


def run_async(coro: object) -> None:
    """Helper to run async coroutines from sync Typer commands."""
    asyncio.run(coro)  # type: ignore[arg-type]


@app.command()
def info(
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
    json_output: JsonOption = False,
) -> None:
    """Show server info and capabilities."""

    async def _info() -> None:
        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        result = await client.get_server_info()
        if json_output:
            console.print_json(data=result)
        else:
            print_info(result)

    try:
        run_async(_info())
    except AnvilError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command("list-tools")
def list_tools(
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
    json_output: JsonOption = False,
    detail: Annotated[
        str | None,
        typer.Option(
            "--detail",
            "-d",
            help="Show detailed info for a specific tool",
        ),
    ] = None,
) -> None:
    """List available tools from the server."""

    async def _list() -> None:
        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        tools = await client.list_tools()

        if detail:
            # Find the specific tool
            tool = next((t for t in tools if t["name"] == detail), None)
            if tool:
                if json_output:
                    console.print_json(data=tool)
                else:
                    print_tool_detail(tool)
            else:
                print_error(f"Tool '{detail}' not found")
                raise typer.Exit(1)
        elif json_output:
            console.print_json(data=tools)
        else:
            print_tools(tools)

    try:
        run_async(_list())
    except AnvilError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command()
def call(
    tool: Annotated[str, typer.Argument(help="Tool name to call")],
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
    arg: Annotated[
        list[str] | None,
        typer.Option(
            "--arg",
            "-a",
            help="Tool argument in key=value format (can be repeated)",
        ),
    ] = None,
    json_args: Annotated[
        str | None,
        typer.Option(
            "--json-args",
            help="Tool arguments as JSON string",
        ),
    ] = None,
    json_output: JsonOption = False,
) -> None:
    """Call a tool with arguments.

    Arguments can be provided in two ways:

    1. Key=value pairs: anvil call get_weather --arg city=Berlin --arg units=metric

    2. JSON string: anvil call get_weather --json-args '{"city": "Berlin"}'
    """

    async def _call() -> None:
        # Parse arguments
        arguments: dict = {}

        if json_args:
            try:
                arguments = json.loads(json_args)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON: {e}")
                raise typer.Exit(1) from e
        elif arg:
            for a in arg:
                if "=" not in a:
                    print_error(f"Invalid argument format: '{a}'. Use key=value format.")
                    raise typer.Exit(1)

                key, _, value = a.partition("=")
                # Try to parse value as JSON for complex types
                try:
                    arguments[key] = json.loads(value)
                except json.JSONDecodeError:
                    arguments[key] = value

        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        result = await client.call_tool(tool, arguments or None)

        if json_output:
            console.print_json(data=result)
        else:
            print_result(result)

    try:
        run_async(_call())
    except AnvilError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command("list-resources")
def list_resources(
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
    json_output: JsonOption = False,
) -> None:
    """List available resources from the server."""

    async def _list() -> None:
        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        resources = await client.list_resources()
        if json_output:
            console.print_json(data=resources)
        else:
            print_resources(resources)

    try:
        run_async(_list())
    except AnvilError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command("list-prompts")
def list_prompts(
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
    json_output: JsonOption = False,
) -> None:
    """List available prompts from the server."""

    async def _list() -> None:
        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        prompts = await client.list_prompts()
        if json_output:
            console.print_json(data=prompts)
        else:
            print_prompts(prompts)

    try:
        run_async(_list())
    except AnvilError as e:
        print_error(str(e))
        raise typer.Exit(1) from e


@app.command()
def ping(
    server: ServerOption = "http://localhost:8000/mcp",
    header: HeaderOption = None,
) -> None:
    """Check if server is responsive."""

    async def _ping() -> None:
        headers = parse_headers(header)
        client = AnvilClient(server, headers=headers)
        if await client.ping():
            console.print(f"[green]Server at {server} is responsive[/green]")
        else:
            console.print(f"[red]Server at {server} is not responding[/red]")
            raise typer.Exit(1)

    run_async(_ping())


@app.command()
def ui(
    server: ServerOption = "http://localhost:8000/mcp",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            help="Port for the UI server",
        ),
    ] = 5000,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Host to bind to",
        ),
    ] = "127.0.0.1",
) -> None:
    """Launch interactive web UI for testing MCP servers."""
    from forge_anvil.ui.server import run_ui_server

    run_ui_server(host=host, port=port, default_server=server)


if __name__ == "__main__":
    app()
