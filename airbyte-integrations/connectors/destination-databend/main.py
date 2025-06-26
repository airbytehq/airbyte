#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_databend import DestinationDatabend


if __name__ == "__main__":
    DestinationDatabend().run(sys.argv[1:])
