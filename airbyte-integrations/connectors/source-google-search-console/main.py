#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_search_console import SourceGoogleSearchConsole

if __name__ == "__main__":
    source = SourceGoogleSearchConsole()
    launch(source, sys.argv[1:])
