#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coingecko_coins import SourceCoingeckoCoins

if __name__ == "__main__":
    source = SourceCoingeckoCoins()
    launch(source, sys.argv[1:])
