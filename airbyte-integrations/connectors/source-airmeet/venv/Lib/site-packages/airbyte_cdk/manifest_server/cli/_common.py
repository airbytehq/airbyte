# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Common utilities for manifest server CLI commands."""

import sys

import rich_click as click

# Import server dependencies with graceful fallback
try:
    import ddtrace  # noqa: F401
    import fastapi  # noqa: F401
    import uvicorn  # noqa: F401

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


def check_manifest_server_dependencies() -> None:
    """Check if manifest-server dependencies are installed."""
    if not FASTAPI_AVAILABLE:
        click.echo(
            "❌ Manifest runner dependencies not found. Please install with:\n\n"
            "  pip install airbyte-cdk[manifest-server]\n"
            "  # or\n"
            "  poetry install --extras manifest-server\n",
            err=True,
        )
        sys.exit(1)
