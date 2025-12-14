"""Rich output formatting helpers for Anvil CLI."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def print_info(info: dict[str, Any]) -> None:
    """Print server info in a panel."""
    lines = [
        f"[bold]Name:[/bold] {info.get('name', 'Unknown')}",
        f"[bold]Version:[/bold] {info.get('version', 'Unknown')}",
        f"[bold]Protocol:[/bold] {info.get('protocol_version', 'Unknown')}",
    ]

    capabilities = info.get("capabilities", {})
    if capabilities:
        caps_str = ", ".join(k for k, v in capabilities.items() if v)
        lines.append(f"[bold]Capabilities:[/bold] {caps_str or 'None'}")

    instructions = info.get("instructions")
    if instructions:
        lines.append("")
        lines.append("[bold]Instructions:[/bold]")
        lines.append(f"  {instructions}")

    console.print(Panel("\n".join(lines), title="Server Info", border_style="blue"))


def print_tools(tools: list[dict[str, Any]]) -> None:
    """Print tools in a table format."""
    if not tools:
        console.print("[yellow]No tools available[/yellow]")
        return

    table = Table(title="Available Tools", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")

    for tool in tools:
        table.add_row(
            tool.get("name", ""),
            tool.get("description", "") or "[dim]No description[/dim]",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(tools)} tool(s)[/dim]")


def print_tool_detail(tool: dict[str, Any]) -> None:
    """Print detailed tool information including schema."""
    console.print(f"\n[bold green]{tool.get('name', 'Unknown')}[/bold green]")

    description = tool.get("description")
    if description:
        console.print(f"  {description}")

    schema = tool.get("input_schema", {})
    if schema:
        console.print("\n[bold]Input Schema:[/bold]")
        syntax = Syntax(
            json.dumps(schema, indent=2),
            "json",
            theme="monokai",
            line_numbers=False,
        )
        console.print(syntax)


def print_resources(resources: list[dict[str, Any]]) -> None:
    """Print resources in a table format."""
    if not resources:
        console.print("[yellow]No resources available[/yellow]")
        return

    table = Table(title="Available Resources", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("URI", style="blue")
    table.add_column("MIME Type")
    table.add_column("Description")

    for resource in resources:
        table.add_row(
            resource.get("name", ""),
            resource.get("uri", ""),
            resource.get("mime_type", "") or "[dim]-[/dim]",
            resource.get("description", "") or "[dim]No description[/dim]",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(resources)} resource(s)[/dim]")


def print_prompts(prompts: list[dict[str, Any]]) -> None:
    """Print prompts in a table format."""
    if not prompts:
        console.print("[yellow]No prompts available[/yellow]")
        return

    table = Table(title="Available Prompts", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Arguments")

    for prompt in prompts:
        args = prompt.get("arguments", [])
        args_str = (
            ", ".join(f"[cyan]{a['name']}[/cyan]{'*' if a.get('required') else ''}" for a in args)
            if args
            else "[dim]None[/dim]"
        )

        table.add_row(
            prompt.get("name", ""),
            prompt.get("description", "") or "[dim]No description[/dim]",
            args_str,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(prompts)} prompt(s). * = required argument[/dim]")


def print_result(result: dict[str, Any]) -> None:
    """Print tool call result."""
    is_error = result.get("is_error", False)
    content = result.get("content", [])

    if is_error:
        console.print("[bold red]Error:[/bold red]")

    for item in content:
        item_type = item.get("type", "text")

        if item_type == "text":
            text = item.get("text", "")
            # Try to parse as JSON for pretty printing
            try:
                data = json.loads(text)
                syntax = Syntax(
                    json.dumps(data, indent=2),
                    "json",
                    theme="monokai",
                    line_numbers=False,
                )
                console.print(syntax)
            except json.JSONDecodeError:
                if is_error:
                    console.print(f"[red]{text}[/red]")
                else:
                    console.print(text)

        elif item_type == "image":
            mime_type = item.get("mime_type", "image/png")
            console.print(f"[dim][Image: {mime_type}][/dim]")

        else:
            console.print(f"[dim][{item_type}][/dim]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")
