#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_typesense import DestinationTypesense


if __name__ == "__main__":
    DestinationTypesense().run(sys.argv[1:])
