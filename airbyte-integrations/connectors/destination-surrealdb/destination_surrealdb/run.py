#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import sys

from destination_surrealdb import DestinationSurrealDB


def run() -> None:
    DestinationSurrealDB().run(sys.argv[1:])


if __name__ == "__main__":
    run()
