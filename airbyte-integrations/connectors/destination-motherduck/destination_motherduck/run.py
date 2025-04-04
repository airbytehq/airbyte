# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys

from destination_motherduck import DestinationMotherDuck


def run() -> None:
    DestinationMotherDuck().run(sys.argv[1:])


if __name__ == "__main__":
    run()
