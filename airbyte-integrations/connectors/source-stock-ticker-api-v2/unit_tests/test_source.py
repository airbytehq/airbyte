#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_stock_ticker_api_v2.source import SourceStockTickerApiV2


def test_check_connection(mocker):
    source = SourceStockTickerApiV2()
    logger_mock, config_mock = MagicMock(), MagicMock()

    source.check_connection(logger_mock, config_mock)

    checked_properties = {args.args[0] for args in config_mock.get.mock_calls if args.args}

    assert "api_key" in checked_properties, "Config must contain api_key property"
    assert "stock_ticker" in checked_properties, "Config must contain stock_ticker property"


def test_streams(mocker):
    source = SourceStockTickerApiV2()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
