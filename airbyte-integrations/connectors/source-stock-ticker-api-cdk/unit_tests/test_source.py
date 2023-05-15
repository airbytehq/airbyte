#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock

import pytest
from source_stock_ticker_api_cdk.source import SourceStockTickerApiCdk

CONFIG = {
    "api_key": "api_key",
    "stock_ticker": "TSLA",
    "start_date": "2023-01-01"
}


@pytest.mark.parametrize(
    ("response_code", "check_result"),
    [
        (200, (True, None)),
        (403, (False, "API Key is incorrect.")),
        (404, (False, "Input configuration is incorrect. Please verify the input stock ticker and API key."))
    ],
)
def test_check_connection(response_code, check_result):
    source = SourceStockTickerApiCdk()
    with mock.patch("requests.get") as http_get:
        http_get.side_effect = [mock.Mock(status_code=response_code)]
        assert source.check_connection(mock.MagicMock(), CONFIG) == check_result
        assert http_get.call_count == 1


def test_streams():
    source = SourceStockTickerApiCdk()
    streams = source.streams(CONFIG)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
