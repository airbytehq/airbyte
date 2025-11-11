# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Info command for the manifest server CLI."""

from typing import Any, Optional

import rich_click as click

# Import server dependencies with graceful fallback
fastapi: Optional[Any] = None
uvicorn: Optional[Any] = None

try:
    import fastapi  # type: ignore[no-redef]
    import uvicorn  # type: ignore[no-redef]

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@click.command()
def info() -> None:
    """Show manifest server information and status."""
    if FASTAPI_AVAILABLE and fastapi is not None and uvicorn is not None:
        click.echo("✅ Manifest runner dependencies are installed")
        click.echo(f"   FastAPI version: {fastapi.__version__}")
        click.echo(f"   Uvicorn version: {uvicorn.__version__}")
    else:
        click.echo("❌ Manifest runner dependencies not installed")
        click.echo("   Install with: pip install airbyte-cdk[manifest-server]")
