#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_cumulio import DestinationCumulio


if __name__ == "__main__":
    DestinationCumulio().run(sys.argv[1:])
