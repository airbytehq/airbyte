#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_firebolt import DestinationFirebolt

if __name__ == "__main__":
    DestinationFirebolt().run(sys.argv[1:])
