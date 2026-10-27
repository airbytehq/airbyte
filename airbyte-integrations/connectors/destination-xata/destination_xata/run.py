#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_xata import DestinationXata


def run() -> None:
    DestinationXata().run(sys.argv[1:])


if __name__ == "__main__":
    run()
