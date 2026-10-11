# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from destination_convex import DestinationConvex


def run():
    DestinationConvex().run(sys.argv[1:])


if __name__ == "__main__":
    run()
