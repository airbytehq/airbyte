#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_cumulio import DestinationCumulio


def run() -> None:
    DestinationCumulio().run(sys.argv[1:])


if __name__ == "__main__":
    run()
