#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_kyriba.source import IncrementalKyribaStream

from .test_streams import config


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalKyribaStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalKyribaStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalKyribaStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    expected_cursor_field = "updateDateTime"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    inputs = {
        "current_stream_state": {"updateDateTime": "2022-01-01T00:00:00Z"},
        "latest_record": {"updateDateTime": "2022-01-01T00:00:01Z"},
    }
    expected_state = {"updateDateTime": "2022-01-01T00:00:01Z"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalKyribaStream, "cursor_field", "dummy_field")
    stream = IncrementalKyribaStream(**config())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_all_request_params(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    inputs = {"stream_state": {"updateDateTime": "2022-01-01T00:00:00Z"}, "stream_slice": {}, "next_page_token": {"page.offset": 100}}
    expected = {"sort": "updateDateTime", "page.offset": 100, "filter": "updateDateTime=gt='2022-01-01T00:00:00Z'"}
    assert stream.request_params(**inputs) == expected


def test_min_request_params(patch_incremental_base_class):
    stream = IncrementalKyribaStream(**config())
    inputs = {"stream_state": {}, "stream_slice": {}, "next_page_token": {}}
    expected = {"sort": "updateDateTime", "filter": "updateDateTime=gt='2022-01-01T00:00:00Z'"}
    assert stream.request_params(**inputs) == expected
