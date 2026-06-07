# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys

from destination_biggeo import DestinationBiggeo


def run():
    """Run the destination."""
    DestinationBiggeo().run(sys.argv[1:])


if __name__ == "__main__":
    run()
