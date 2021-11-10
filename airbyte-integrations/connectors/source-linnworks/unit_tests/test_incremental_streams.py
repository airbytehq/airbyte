#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.models import SyncMode
from source_linnworks.streams import IncrementalLinnworksStream


@pytest.fixture
def patch_incremental_base_class(mocker):
    mocker.patch.object(IncrementalLinnworksStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalLinnworksStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalLinnworksStream, "cursor_field", "test_cursor_field")
    mocker.patch.object(IncrementalLinnworksStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    expected_cursor_field = "test_cursor_field"
    assert stream.cursor_field == expected_cursor_field


@pytest.mark.parametrize(
    ("inputs", "expected_state"),
    [
        (
            {
                "current_stream_state": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:56",
                },
                "latest_record": {},
            },
            {"test_cursor_field": "2021-01-01T01:02:34+01:56"},
        ),
        (
            {
                "current_stream_state": {},
                "latest_record": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:56",
                },
            },
            {"test_cursor_field": "2021-01-01T01:02:34+01:56"},
        ),
        (
            {
                "current_stream_state": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:56",
                },
                "latest_record": {
                    "test_cursor_field": "2021-01-01T01:02:34+01:57",
                },
            },
            {"test_cursor_field": "2021-01-01T01:02:34+01:57"},
        ),
    ],
)
def test_get_updated_state(patch_incremental_base_class, inputs, expected_state):
    stream = IncrementalLinnworksStream()
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalLinnworksStream, "cursor_field", "dummy_field")
    stream = IncrementalLinnworksStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalLinnworksStream()
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
