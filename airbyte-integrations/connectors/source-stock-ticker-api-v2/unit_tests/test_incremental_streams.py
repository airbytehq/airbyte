#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_stock_ticker_api_v2.source import IncrementalStockTickerApiV2Stream, Ticker


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalStockTickerApiV2Stream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalStockTickerApiV2Stream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalStockTickerApiV2Stream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = Ticker("AAA", "2022-02-01")
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    fake_date = "2022-02-01"
    last_date = "2022-10-30"
    stream = Ticker("AAA", fake_date)

    inputs = {
        "current_stream_state": {"date": fake_date},
        "latest_record": {"date": last_date},
    }

    expected_state = {"date": last_date}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalStockTickerApiV2Stream()
    # TODO: replace this with your input parameters
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalStockTickerApiV2Stream, "cursor_field", "dummy_field")
    stream = IncrementalStockTickerApiV2Stream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalStockTickerApiV2Stream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalStockTickerApiV2Stream()
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
