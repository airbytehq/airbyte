#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest

from source_stock_ticker_api_cdk.source import StockPrices


@pytest.fixture
def config() -> dict:
    return {
        "api_key": "api_key",
        "stock_ticker": "stock_ticker",
        "start_date": "2023-09-21",
        "end_date": "2023-09-25",
        "multiplier": 1,
        "timespan": "day",
    }


@pytest.fixture
def response_object() -> dict:
    return {
        "results": [{"c": 111.11, "t": 1695614400000}],
        "resultsCount": 1,
        "ticker": "TCKR",
    }


@pytest.fixture
def patch_base_class(mocker) -> None:
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(StockPrices, "path", "v0/example_endpoint")
    mocker.patch.object(StockPrices, "primary_key", "test_primary_key")
    mocker.patch.object(StockPrices, "__abstractmethods__", set())
