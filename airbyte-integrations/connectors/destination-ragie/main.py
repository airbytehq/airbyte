#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from destination_ragie import DestinationRagie


if __name__ == "__main__":
    DestinationRagie().run(sys.argv[1:])
