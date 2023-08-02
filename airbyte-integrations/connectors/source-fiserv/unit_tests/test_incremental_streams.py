#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_fiserv.source import IncrementalFiservStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalFiservStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalFiservStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalFiservStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalFiservStream()
    expected_cursor_field = "last_sync_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalFiservStream()
    inputs = {"current_stream_state": {"last_sync_at": "2023-07-25"}, "latest_record" : { "last_sync_at": "2023-07-26"}}
    expected_state = {"last_sync_at": "2023-07-26"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalFiservStream()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["last_sync_at"], "stream_state": {"last_sync_at": "2023-07-25"}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [{"last_sync_at": "2023-07-25"}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalFiservStream, "cursor_field", "dummy_field")
    stream = IncrementalFiservStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalFiservStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalFiservStream()
    expected_checkpoint_interval = 1000
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
