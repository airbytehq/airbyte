#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coingecko_coins import SourceCoingeckoCoins


def run():
    source = SourceCoingeckoCoins()
    launch(source, sys.argv[1:])
