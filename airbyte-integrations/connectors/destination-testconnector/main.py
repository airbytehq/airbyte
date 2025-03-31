#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from destination_testconnector import DestinationTestconnector

if __name__ == "__main__":
    DestinationTestconnector().run(sys.argv[1:])
