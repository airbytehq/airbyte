#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_search_console import SourceGoogleSearchConsole

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleSearchConsole()
    launch(source, sys.argv[1:])
