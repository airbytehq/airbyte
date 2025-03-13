# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_pgvector import DestinationPGVector


def run() -> None:
    DestinationPGVector().run(sys.argv[1:])


if __name__ == "__main__":
    run()
