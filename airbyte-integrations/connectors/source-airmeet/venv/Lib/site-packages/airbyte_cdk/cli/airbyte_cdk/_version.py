# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Version information for the Airbyte CDK CLI."""

from airbyte_cdk import __version__


def print_version(short: bool = False) -> None:
    """Print the version of the Airbyte CDK CLI."""

    if short:
        print(__version__)
    else:
        print(f"Airbyte CDK version: {__version__}")
