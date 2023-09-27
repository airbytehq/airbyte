#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_tally import DestinationTally

if __name__ == "__main__":
    DestinationTally().run(sys.argv[1:])
