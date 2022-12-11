#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coin_api import SourceCoinApi

if __name__ == "__main__":
    source = SourceCoinApi()
    launch(source, sys.argv[1:])
