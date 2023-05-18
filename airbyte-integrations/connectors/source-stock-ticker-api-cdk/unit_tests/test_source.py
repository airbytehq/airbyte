#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_stock_ticker_api_cdk.source import SourceStockTickerApiCdk

CONFIG = {
    "api_key": "api_key",
    "stock_ticker": "TSLA",
    "start_date": "2023-01-01"
}


def test_streams():
    source = SourceStockTickerApiCdk()
    streams = source.streams(CONFIG)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
