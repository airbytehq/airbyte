#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_stock_ticker_api_cdk.source import SourceStockTickerApiCDK, StockPrices


def test_check_connection(requests_mock, response_object, config):
    source = SourceStockTickerApiCDK()
    stream = StockPrices(config)
    requests_mock.get(f"{stream.url_base}{stream.path()}", json=response_object)
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams():
    source = SourceStockTickerApiCDK()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
