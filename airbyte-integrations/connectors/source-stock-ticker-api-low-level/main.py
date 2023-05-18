#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stock_ticker_api_low_level import SourceStockTickerApiLowLevel

if __name__ == "__main__":
    source = SourceStockTickerApiLowLevel()
    launch(source, sys.argv[1:])
