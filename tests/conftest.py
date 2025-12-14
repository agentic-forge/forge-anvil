"""Pytest configuration and fixtures for Anvil tests."""

import pytest


@pytest.fixture
def mock_server_url() -> str:
    """Default mock server URL for testing."""
    return "http://localhost:8000/mcp"
