# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_pgvector import DestinationPGVector

if __name__ == "__main__":
    DestinationPGVector().run(sys.argv[1:])
