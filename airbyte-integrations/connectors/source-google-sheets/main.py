#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_sheets import SourceGoogleSheets

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleSheets()
    launch(source, sys.argv[1:])
