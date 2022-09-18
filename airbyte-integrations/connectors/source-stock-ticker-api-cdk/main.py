#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stock_ticker_api_cdk import SourceStockTickerApiCdk

if __name__ == "__main__":
    source = SourceStockTickerApiCdk()
    launch(source, sys.argv[1:])
