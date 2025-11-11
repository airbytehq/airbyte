# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Standalone CLI for the Airbyte CDK Manifest Server.

This CLI provides commands for running and managing the manifest server server.

**Installation:**

To use the manifest-server functionality, install the CDK with the manifest-server extra:

```bash
pip install airbyte-cdk[manifest-server]
# or
poetry install --extras manifest-server
```

**Usage:**

```bash
manifest-server start --port 8000
manifest-server info
manifest-server --help
```
"""

import rich_click as click

from ._info import info
from ._openapi import generate_openapi
from ._start import start


@click.group(
    help=__doc__.replace("\n", "\n\n"),  # Render docstring as help text (markdown)
    invoke_without_command=True,
)
@click.pass_context
def cli(
    ctx: click.Context,
) -> None:
    """Airbyte Manifest Server CLI."""

    if ctx.invoked_subcommand is None:
        # If no subcommand is provided, show the help message.
        click.echo(ctx.get_help())
        ctx.exit()


cli.add_command(start)
cli.add_command(info)
cli.add_command(generate_openapi)


def run() -> None:
    """Entry point for the manifest-server CLI."""
    cli()


if __name__ == "__main__":
    run()
