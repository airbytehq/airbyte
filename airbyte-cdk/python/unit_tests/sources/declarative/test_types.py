# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_cdk.sources.declarative.types import DeclarativeStreamSlice


@pytest.mark.parametrize(
    "stream_slice, expected_partition",
    [
        pytest.param(DeclarativeStreamSlice({},{}), {}, id="test_partition_with_empty_partition"),
        pytest.param(DeclarativeStreamSlice(DeclarativeStreamSlice({}, {}), {}), {}, id="test_partition_nested_empty"),
        pytest.param(DeclarativeStreamSlice({"key": "value"}, {}), {"key": "value"}, id="test_partition_with_mapping_partition"),
        pytest.param(DeclarativeStreamSlice({},{"cursor": "value"}), {}, id="test_partition_with_only_cursor"),
        pytest.param(DeclarativeStreamSlice(DeclarativeStreamSlice({}, {}), {"cursor": "value"}), {}, id="test_partition_nested_empty_and_cursor_value_mapping"),
        pytest.param(DeclarativeStreamSlice(DeclarativeStreamSlice({}, {"cursor": "value"}), {}), {}, id="test_partition_nested_empty_and_cursor_value"),
    ]
)
def test_partition(stream_slice, expected_partition):
    partition = stream_slice.partition

    assert partition == expected_partition


@pytest.mark.parametrize(
    "stream_slice, expected_cursor_slice",
    [
        pytest.param(DeclarativeStreamSlice({},{}), {}, id="test_cursor_slice_with_empty_cursor"),
        pytest.param(DeclarativeStreamSlice({}, DeclarativeStreamSlice({}, {})), {}, id="test_cursor_slice_nested_empty"),

        pytest.param(DeclarativeStreamSlice({}, {"key": "value"}), {"key": "value"}, id="test_cursor_slice_with_mapping_cursor_slice"),
        pytest.param(DeclarativeStreamSlice({"partition": "value"}, {}), {}, id="test_cursor_slice_with_only_partition"),
        pytest.param(DeclarativeStreamSlice({"partition": "value"}, DeclarativeStreamSlice({}, {})), {}, id="test_cursor_slice_nested_empty_and_partition_mapping"),
        pytest.param(DeclarativeStreamSlice(DeclarativeStreamSlice({"partition": "value"}, {}), {}), {}, id="test_cursor_slice_nested_empty_and_partition"),
    ]
)
def test_cursor_slice(stream_slice, expected_cursor_slice):
    cursor_slice = stream_slice.cursor_slice

    assert cursor_slice == expected_cursor_slice
