#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_glassflow import DestinationGlassflow


if __name__ == "__main__":
    DestinationGlassflow().run(sys.argv[1:])
