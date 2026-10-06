#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_qdrant import DestinationQdrant


if __name__ == "__main__":
    DestinationQdrant().run(sys.argv[1:])
