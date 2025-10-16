# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.entrypoint import launch
from .destination import DestinationBiggeo


def run():
    """Run the destination."""
    source = DestinationBiggeo()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
