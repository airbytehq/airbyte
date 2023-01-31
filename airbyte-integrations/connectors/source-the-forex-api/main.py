#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_the_forex_api import SourceTheForexApi

if __name__ == "__main__":
    source = SourceTheForexApi()
    launch(source, sys.argv[1:])
