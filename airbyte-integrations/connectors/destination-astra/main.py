#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_astra import DestinationAstra


if __name__ == "__main__":
    DestinationAstra().run(sys.argv[1:])
