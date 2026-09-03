#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from destination_qdrant import DestinationQdrant


def run() -> None:
    DestinationQdrant().run(sys.argv[1:])


if __name__ == "__main__":
    run()
