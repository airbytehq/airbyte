#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stock_ticker_api import SourceStockTickerApi

if __name__ == "__main__":
    source = SourceStockTickerApi()
    launch(source, sys.argv[1:])
