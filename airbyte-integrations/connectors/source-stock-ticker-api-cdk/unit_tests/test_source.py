#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_stock_ticker_api_cdk.source import SourceStockTickerApiCdk


@pytest.fixture(name="config_incorrect")
def config_fixture():
    config = {'api_key': 'api_key', 'stock_ticker': 'stock_ticker'}
    return config


def test_check_connection_incorrect_configuration(mocker, config_incorrect):
    source = SourceStockTickerApiCdk()
    logger_mock, config_mock = MagicMock(), MagicMock(config_incorrect)
    assert source.check_connection(logger_mock, config_mock) == (
        False, {"status": "FAILED",
                "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}
    )


def test_streams(mocker):
    source = SourceStockTickerApiCdk()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
