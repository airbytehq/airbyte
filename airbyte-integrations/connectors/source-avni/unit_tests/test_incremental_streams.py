#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_avni.source import IncrementalAvniStream


@fixture
def patch_incremental_base_class(mocker):

    mocker.patch.object(IncrementalAvniStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalAvniStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalAvniStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):

    stream = IncrementalAvniStream(start_date="",auth_token="")
    expected_cursor_field = "last_modified_at"
    assert stream.cursor_field == expected_cursor_field


def test_update_state(patch_incremental_base_class):

    stream = IncrementalAvniStream(start_date="",auth_token="")
    stream.state = {"last_modified_at":"2000-06-27T04:18:36.914Z"}
    stream.last_record = {"audit":{"Last modified at":"2001-06-27T04:18:36.914Z"}}
    expected_state = {"last_modified_at":"2001-06-27T04:18:36.914Z"}
    stream.update_state()
    assert stream.state == expected_state


def test_stream_slices(patch_incremental_base_class):

    stream = IncrementalAvniStream(start_date="",auth_token="")
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):

    mocker.patch.object(IncrementalAvniStream, "cursor_field", "dummy_field")
    stream = IncrementalAvniStream(start_date="",auth_token="")
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):

    stream = IncrementalAvniStream(start_date="",auth_token="")
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):

    stream = IncrementalAvniStream(start_date="",auth_token="")
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
