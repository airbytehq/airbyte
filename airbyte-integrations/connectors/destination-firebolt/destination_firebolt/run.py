#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import sys

from destination_firebolt import DestinationFirebolt


def run():
    DestinationFirebolt().run(sys.argv[1:])


if __name__ == "__main__":
    run()
