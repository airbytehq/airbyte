# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_weaviate import DestinationWeaviate


def run() -> None:
    DestinationWeaviate().run(sys.argv[1:])


if __name__ == "__main__":
    run()
