# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys

from destination_starrocks.destination import DestinationStarRocks


def run():
    DestinationStarRocks().run(sys.argv[1:])

if __name__ == "__main__":
    run()
