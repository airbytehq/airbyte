#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import sys

from destination_dewey import DestinationDewey


def run() -> None:
    DestinationDewey().run(sys.argv[1:])


if __name__ == "__main__":
    run()
