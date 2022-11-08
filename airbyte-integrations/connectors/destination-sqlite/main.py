#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_sqlite import DestinationSqlite

if __name__ == "__main__":
    DestinationSqlite().run(sys.argv[1:])
