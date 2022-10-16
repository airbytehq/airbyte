#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_trello.source import IncrementalTrelloStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalTrelloStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalTrelloStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalTrelloStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class, config):
    stream = IncrementalTrelloStream(config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, config):
    stream = IncrementalTrelloStream(config)
    expected_cursor_field = "date"
    inputs = {
        "current_stream_state": {expected_cursor_field: "2021-07-12T10:44:09+00:00"},
        "latest_record": {expected_cursor_field: "2021-07-15T10:44:09+00:00"},
    }
    expected_state = {expected_cursor_field: "2021-07-15T10:44:09+00:00"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, config):
    stream = IncrementalTrelloStream(config)
    expected_cursor_field = "date"
    inputs = {
        "sync_mode": SyncMode.incremental,
        "cursor_field": expected_cursor_field,
        "stream_state": {expected_cursor_field: "2021-07-15T10:44:09+00:00"},
    }
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, config):
    mocker.patch.object(IncrementalTrelloStream, "cursor_field", "dummy_field")
    stream = IncrementalTrelloStream(config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, config):
    stream = IncrementalTrelloStream(config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, config):
    stream = IncrementalTrelloStream(config)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
