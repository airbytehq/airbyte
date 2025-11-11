# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Start command for the manifest server CLI."""

import rich_click as click

from ._common import check_manifest_server_dependencies


@click.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind the server to",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    help="Port to bind the server to",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
def start(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI manifest server server."""
    check_manifest_server_dependencies()

    # Import and use the main server function
    from airbyte_cdk.manifest_server.main import run_server

    run_server(
        host=host,
        port=port,
        reload=reload,
    )
