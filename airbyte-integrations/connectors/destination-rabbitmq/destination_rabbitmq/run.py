#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_rabbitmq import DestinationRabbitmq


def run() -> None:
    DestinationRabbitmq().run(sys.argv[1:])


if __name__ == "__main__":
    run()
