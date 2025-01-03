#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_milvus import DestinationMilvus


if __name__ == "__main__":
    DestinationMilvus().run(sys.argv[1:])
