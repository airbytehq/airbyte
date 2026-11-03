#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys

from destination_google_sheets import DestinationGoogleSheets


def run() -> None:
    DestinationGoogleSheets().run(sys.argv[1:])


if __name__ == "__main__":
    run()
