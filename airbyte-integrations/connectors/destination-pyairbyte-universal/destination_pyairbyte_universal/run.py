# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Entry point for the universal destination connector."""

import sys

from airbyte.cli.universal_connector import DestinationPyAirbyteUniversal


def run() -> None:
    """Run the destination connector."""
    DestinationPyAirbyteUniversal().run(sys.argv[1:])


if __name__ == "__main__":
    run()
