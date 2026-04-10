# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from destination_altertable import DestinationAltertable


def run() -> None:
    DestinationAltertable().run(sys.argv[1:])


if __name__ == "__main__":
    run()
