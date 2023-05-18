#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.models import SyncMode
from source_stock_ticker_api_cdk.source import StockPrices


@pytest.fixture
def stream():
    return StockPrices(
        connector=None,
        stock_ticker="TSLA",
        start_date=datetime.datetime.strptime("2022-07-07", "%Y-%m-%d"),
    )

    def test_cursor_field(stream):
        expected_cursor_field = "date"
        assert stream.cursor_field == expected_cursor_field

    def test_stream_slices(stream):
        period = 12
        start_date = datetime.datetime.now() - datetime.timedelta(days=period)
        inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "date", "stream_state": {"date": start_date.strftime("%Y-%m-%d")}}

        dates = []
        while start_date < datetime.datetime.now():
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = (start_date + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            dates.append({"start_date": start_date_str, "end_date": end_date_str})
            start_date += datetime.timedelta(days=8)

        assert list(stream.stream_slices(**inputs)) == dates

    def test_supports_incremental(stream):
        assert stream.supports_incremental

    def test_source_defined_cursor(stream):
        assert stream.source_defined_cursor

    def test_stream_checkpoint_interval(stream):
        expected_checkpoint_interval = None
        assert stream.state_checkpoint_interval == expected_checkpoint_interval
