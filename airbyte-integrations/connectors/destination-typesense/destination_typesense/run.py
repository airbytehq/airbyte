#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

from destination_typesense import DestinationTypesense


def run() -> None:
    DestinationTypesense().run(sys.argv[1:])


if __name__ == "__main__":
    run()
