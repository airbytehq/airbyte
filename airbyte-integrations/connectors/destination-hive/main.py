#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_hive import DestinationHive

if __name__ == "__main__":
    DestinationHive().run(sys.argv[1:])
