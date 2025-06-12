#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_chroma import DestinationChroma


if __name__ == "__main__":
    DestinationChroma().run(sys.argv[1:])
