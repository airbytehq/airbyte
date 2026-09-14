# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import sys

from destination_milvus import DestinationMilvus


def run() -> None:
    DestinationMilvus().run(sys.argv[1:])


if __name__ == "__main__":
    run()
