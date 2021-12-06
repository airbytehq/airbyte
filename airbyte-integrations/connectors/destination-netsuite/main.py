#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_netsuite import DestinationNetsuite

if __name__ == "__main__":
    DestinationNetsuite().run(sys.argv[1:])
