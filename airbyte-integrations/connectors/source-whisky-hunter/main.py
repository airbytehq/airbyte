#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_whisky_hunter import SourceWhiskyHunter

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceWhiskyHunter()
    launch(source, sys.argv[1:])
