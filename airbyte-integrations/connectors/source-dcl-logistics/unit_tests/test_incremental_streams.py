#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from pytest import fixture
from source_dcl_logistics.source import DEFAULT_CURSOR, IncrementalDclLogisticsStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalDclLogisticsStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalDclLogisticsStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalDclLogisticsStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalDclLogisticsStream()
    expected_cursor_field = DEFAULT_CURSOR
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalDclLogisticsStream()
    inputs = {"current_stream_state": None, "latest_record": {DEFAULT_CURSOR: "2022-02-01T00:00:00"}}
    expected_state = {DEFAULT_CURSOR: "2022-02-01T00:00:00"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalDclLogisticsStream, "cursor_field", "dummy_field")
    stream = IncrementalDclLogisticsStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalDclLogisticsStream()
    assert stream.source_defined_cursor
