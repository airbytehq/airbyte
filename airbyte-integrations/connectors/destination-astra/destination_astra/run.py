# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from destination_astra import DestinationAstra


def run() -> None:
    DestinationAstra().run(sys.argv[1:])


if __name__ == "__main__":
    run()
