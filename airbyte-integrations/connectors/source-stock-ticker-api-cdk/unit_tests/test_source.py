#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_stock_ticker_api_cdk.source import SourceStockTickerApiCdk

CONFIG = {
    "api_key": "api_key",
    "stock_ticker": "TSLA",
    "start_date": "2023-01-01",
    "time_step": 30
}


def test_check_connection():
    source = SourceStockTickerApiCdk()
    fake_info_record = {"date":"2023-05-05","stock_ticker":"TSLA","price":170.06}
    with patch("source_stock_ticker_api_cdk.source.StockPrices.read_records", MagicMock(return_value=iter([fake_info_record]))):
        with patch("source_stock_ticker_api_cdk.source.StockPrices.stream_slices", MagicMock(return_value=[0])):
            logger_mock = MagicMock()
            assert source.check_connection(logger_mock, CONFIG) == (True, None)


def test_streams():
    source = SourceStockTickerApiCdk()
    streams = source.streams(CONFIG)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
