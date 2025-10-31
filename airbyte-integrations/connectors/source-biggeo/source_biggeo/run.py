# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Entrypoint for the BigGeo source connector."""

import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceBiggeo


def run():
    """Run the source connector."""
    source = SourceBiggeo()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
