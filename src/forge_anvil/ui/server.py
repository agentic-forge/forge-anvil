"""Simple HTTP server for serving the Anvil web UI."""

from __future__ import annotations

import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Path to the UI HTML file
UI_DIR = Path(__file__).parent
UI_HTML_PATH = UI_DIR / "index.html"


class UIHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves the Anvil UI with injected default server."""

    default_server: str = "http://localhost:8000/mcp"

    def __init__(self, *args, default_server: str = "http://localhost:8000/mcp", **kwargs) -> None:
        """Initialize handler with default server URL."""
        UIHandler.default_server = default_server
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path in {"/", "/index.html"}:
            self._serve_ui()
        else:
            super().do_GET()

    def _serve_ui(self) -> None:
        """Serve the UI HTML with injected default server URL."""
        try:
            html = UI_HTML_PATH.read_text()
            # Inject the default server URL
            html = html.replace("{{DEFAULT_SERVER}}", self.default_server)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html.encode())))
            self.end_headers()
            self.wfile.write(html.encode())
        except FileNotFoundError:
            self.send_error(404, "UI file not found")

    def log_message(self, format: str, *args) -> None:
        """Suppress default logging."""
        _ = format, args  # Unused


def run_ui_server(
    host: str = "127.0.0.1",
    port: int = 5000,
    default_server: str = "http://localhost:8000/mcp",
) -> None:
    """Run the UI server.

    Args:
        host: Host to bind to
        port: Port to listen on
        default_server: Default MCP server URL to inject into the UI
    """
    handler = partial(UIHandler, default_server=default_server)

    server = HTTPServer((host, port), handler)

    url = f"http://{host}:{port}"
    print(f"Starting Anvil UI at {url}")
    print(f"Default MCP server: {default_server}")
    print("Press Ctrl+C to stop\n")

    # Open browser
    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
