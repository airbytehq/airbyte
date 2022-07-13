#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_exchange_rate_api.source import IncrementalExchangeRateApiStream, HistoricalRates


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalExchangeRateApiStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalExchangeRateApiStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalExchangeRateApiStream, "__abstractmethods__", set())

    return {
        "config": {
            "base": "USD",
            "symbols": ["USD", "EUR"],
            "start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d")
        }
    }


def test_cursor_field(patch_incremental_base_class):
    stream = HistoricalRates(config=patch_incremental_base_class["config"])
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = HistoricalRates(config=patch_incremental_base_class["config"])
    record = {
        'success': True,
        'timestamp': int(datetime.datetime.now().timestamp()),
        'base': '<base>',
        'date': datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
        'rates': {'<base>': 1}
    }
    inputs = {
        "current_stream_state": {},
        "latest_record": record
    }
    expected_state = {"date": datetime.datetime.strptime(record["date"], "%Y-%m-%d").date()}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = HistoricalRates(config=patch_incremental_base_class["config"])
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [
        {
            "date": patch_incremental_base_class["config"]["start_date"],
        },
        {
            "date": datetime.datetime.strftime(
                datetime.datetime.strptime(patch_incremental_base_class["config"]["start_date"], "%Y-%m-%d") + datetime.timedelta(days=1),
                "%Y-%m-%d"
            )
        }
    ]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalExchangeRateApiStream, "cursor_field", "dummy_field")
    stream = IncrementalExchangeRateApiStream(config=patch_incremental_base_class["config"])
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalExchangeRateApiStream(config=patch_incremental_base_class["config"])
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalExchangeRateApiStream(config=patch_incremental_base_class["config"])
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
