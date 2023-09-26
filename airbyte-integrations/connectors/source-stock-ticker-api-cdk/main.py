#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stock_ticker_api_cdk import SourceStockTickerApiCDK

if __name__ == "__main__":
    source = SourceStockTickerApiCDK()
    launch(source, sys.argv[1:])
