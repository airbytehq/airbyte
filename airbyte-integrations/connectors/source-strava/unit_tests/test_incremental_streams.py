#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_strava.streams import IncrementalStravaStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalStravaStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalStravaStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalStravaStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class, start_date):
    stream = IncrementalStravaStream(start_date)
    expected_cursor_field = "start_date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, start_date):
    stream = IncrementalStravaStream(start_date)
    expected_cursor_field = "start_date"
    inputs = {
        "current_stream_state": {expected_cursor_field: "2015-01-01T00:00:00Z"},
        "latest_record": {expected_cursor_field: "2016-01-01T00:00:00Z"},
    }
    expected_state = {"start_date": "2016-01-01T00:00:00Z"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, start_date):
    stream = IncrementalStravaStream(start_date)
    cursor_field = "start_date"
    epoch_string = "1970-01-01T00:00:00Z"
    epoch_timestamp = 0
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [cursor_field], "stream_state": {cursor_field: epoch_string}}
    expected_stream_slice = [{"after": epoch_timestamp}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, start_date):
    mocker.patch.object(IncrementalStravaStream, "cursor_field", "dummy_field")
    stream = IncrementalStravaStream(start_date)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, start_date):
    stream = IncrementalStravaStream(start_date)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, start_date):
    stream = IncrementalStravaStream(start_date)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
