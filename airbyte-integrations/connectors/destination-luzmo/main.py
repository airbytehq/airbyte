#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_luzmo import DestinationLuzmo

if __name__ == "__main__":
    DestinationLuzmo().run(sys.argv[1:])
