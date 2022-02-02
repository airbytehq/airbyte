#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_ngpvan import DestinationNGPVAN

if __name__ == "__main__":
    DestinationNGPVAN().run(sys.argv[1:])
