#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_google_sheets import DestinationGoogleSheets


if __name__ == "__main__":
    DestinationGoogleSheets().run(sys.argv[1:])
