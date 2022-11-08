#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_kvdb import DestinationKvdb

if __name__ == "__main__":
    DestinationKvdb().run(sys.argv[1:])
