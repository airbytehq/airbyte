# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys

from destination_duckdb import DestinationDuckdb


def run():
    DestinationDuckdb().run(sys.argv[1:])


if __name__ == "__main__":
    run()
