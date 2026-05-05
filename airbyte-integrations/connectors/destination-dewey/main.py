#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import sys

from destination_dewey import DestinationDewey


if __name__ == "__main__":
    DestinationDewey().run(sys.argv[1:])
