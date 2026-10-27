#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_databend import DestinationDatabend


def run() -> None:
    DestinationDatabend().run(sys.argv[1:])


if __name__ == "__main__":
    run()
