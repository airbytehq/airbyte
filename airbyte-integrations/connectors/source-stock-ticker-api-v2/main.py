#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stock_ticker_api_v2 import SourceStockTickerApiV2

if __name__ == "__main__":
    source = SourceStockTickerApiV2()
    launch(source, sys.argv[1:])
