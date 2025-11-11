# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Manifest related commands.

Coming soon.

This module is planned to provide a command line interface (CLI) for validating
Airbyte CDK manifests.
"""

import rich_click as click


@click.group(
    name="manifest",
    help=__doc__.replace("\n", "\n\n"),  # Render docstring as help text (markdown)
)
def manifest_cli_group() -> None:
    """Manifest related commands."""
    pass


__all__ = [
    "manifest_cli_group",
]
