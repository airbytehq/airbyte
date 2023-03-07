#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_whisky_hunter import SourceWhiskyHunter

if __name__ == "__main__":
    source = SourceWhiskyHunter()
    launch(source, sys.argv[1:])
