#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from google_sheets_source import GoogleSheetsSource

if __name__ == "__main__":
    source = GoogleSheetsSource()
    launch(source, sys.argv[1:])
