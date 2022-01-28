#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_ngpvan import DestinationNgpvan

if __name__ == "__main__":
    DestinationNgpvan().run(sys.argv[1:])
