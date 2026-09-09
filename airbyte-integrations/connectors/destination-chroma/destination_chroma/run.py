# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_chroma import DestinationChroma


def run() -> None:
    DestinationChroma().run(sys.argv[1:])


if __name__ == "__main__":
    run()
