#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_coingecko_coins import SourceCoingeckoCoins

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceCoingeckoCoins()
    launch(source, sys.argv[1:])
