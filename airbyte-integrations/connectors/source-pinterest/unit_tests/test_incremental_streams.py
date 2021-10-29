#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_pinterest.source import IncrementalPinterestStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalPinterestStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalPinterestStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalPinterestStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalPinterestStream()
    expected_cursor_field = None
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalPinterestStream()
    inputs = {"current_stream_state": {"date": "2021-10-22"}, "latest_record": {"date": "2021-10-22"}}
    expected_state = {"date": "2021-10-22"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalPinterestStream()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "date", "stream_state": {"date": "2021-10-22"}}
    expected_stream_slice = [{"start_date": "", "end_date": ""}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalPinterestStream, "cursor_field", "dummy_field")
    stream = IncrementalPinterestStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalPinterestStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalPinterestStream()
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
