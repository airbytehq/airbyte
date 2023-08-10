#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pendulum

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_fiserv.source import IncrementalFiservStream


config = {
    "start_date": "2023-08-04",
    "api_key": "api_key",
    "api_secret": "api_secret",
}


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalFiservStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalFiservStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalFiservStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalFiservStream(**config)
    expected_cursor_field = "last_sync_at"
    assert stream.cursor_field == expected_cursor_field


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalFiservStream(**config)
    start_date = "20230725"
    end_date = pendulum.yesterday(tz="utc").strftime("%Y%m%d")
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["last_sync_at"], "stream_state": {"last_sync_at": start_date}}
    expected_stream_slice = list(stream._chunk_date_range(start_date, end_date))
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalFiservStream, "cursor_field", "last_sync_at")
    stream = IncrementalFiservStream(**config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalFiservStream(**config)
    assert stream.source_defined_cursor
