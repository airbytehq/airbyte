#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_convex import DestinationConvex


if __name__ == "__main__":
    DestinationConvex().run(sys.argv[1:])
