#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import sys

from destination_surrealdb import DestinationSurrealDB


if __name__ == "__main__":
    DestinationSurrealDB().run(sys.argv[1:])
