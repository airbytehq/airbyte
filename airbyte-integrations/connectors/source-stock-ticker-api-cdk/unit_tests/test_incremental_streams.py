#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import SyncMode
from source_stock_ticker_api_cdk.source import StockPrices


def test_cursor_field(patch_base_class, config):
    stream = StockPrices(config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices(patch_base_class, config):
    stream = StockPrices(config)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "date", "stream_state": {"date": "2023-09-23"}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_base_class, mocker, config):
    mocker.patch.object(StockPrices, "cursor_field", "dummy_field")
    stream = StockPrices(config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_base_class, config):
    stream = StockPrices(config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_base_class, config):
    stream = StockPrices(config)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_date"),
    [
        ({"date": "2023-09-21"}, {"date": "2023-09-22", "stock_ticker": "TCKR", "price": 111.11}, "2023-09-22"),
        ({"date": "2023-09-22"}, {"date": "2023-09-21", "stock_ticker": "TCKR", "price": 111.11}, "2023-09-22"),
        ({}, {"date": "2023-09-22", "stock_ticker": "TCKR", "price": 111.11}, "2023-09-22"),
    ]
)
def test_get_updated_state(patch_base_class, config, current_stream_state, latest_record, expected_date):
    stream = StockPrices(config)
    inputs = {"current_stream_state": current_stream_state, "latest_record": latest_record}
    expected_state = {"date": expected_date}
    assert stream.get_updated_state(**inputs) == expected_state
