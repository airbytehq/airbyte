#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_xata import DestinationXata


if __name__ == "__main__":
    DestinationXata().run(sys.argv[1:])
