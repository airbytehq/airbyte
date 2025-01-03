#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_pinecone import DestinationPinecone


if __name__ == "__main__":
    DestinationPinecone().run(sys.argv[1:])
