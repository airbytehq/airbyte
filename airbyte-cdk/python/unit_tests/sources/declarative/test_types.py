import pytest
from airbyte_cdk.sources.declarative.types import PerPartitionStreamSlice


@pytest.mark.parametrize(
    "stream_slice, expected_partition",
    [
        pytest.param(PerPartitionStreamSlice({},{}), {}, id="test_partition_with_empty_partition"),
        pytest.param(PerPartitionStreamSlice(PerPartitionStreamSlice({}, {}), {}), {}, id="test_partition_nested_empty"),
        pytest.param(PerPartitionStreamSlice({"key": "value"}, {}), {"key": "value"}, id="test_partition_with_mapping_partition"),
        pytest.param(PerPartitionStreamSlice({},{"cursor": "value"}), {}, id="test_partition_with_only_cursor"),
        pytest.param(PerPartitionStreamSlice(PerPartitionStreamSlice({}, {}), {"cursor": "value"}), {}, id="test_partition_nested_empty_and_cursor_value_mapping"),
        pytest.param(PerPartitionStreamSlice(PerPartitionStreamSlice({}, {"cursor": "value"}), {}), {}, id="test_partition_nested_empty_and_cursor_value"),
    ]
)
def test_partition(stream_slice, expected_partition):
    partition = stream_slice.partition

    assert partition == expected_partition

@pytest.mark.parametrize(
    "stream_slice, expected_cursor_slice",
    [
        pytest.param(PerPartitionStreamSlice({},{}), {}, id="test_cursor_slice_with_empty_cursor"),
        pytest.param(PerPartitionStreamSlice({}, PerPartitionStreamSlice({}, {})), {}, id="test_cursor_slice_nested_empty"),

        pytest.param(PerPartitionStreamSlice({}, {"key": "value"}), {"key": "value"}, id="test_cursor_slice_with_mapping_cursor_slice"),
        pytest.param(PerPartitionStreamSlice({"partition": "value"}, {}), {}, id="test_cursor_slice_with_only_partition"),
        pytest.param(PerPartitionStreamSlice({"partition": "value"}, PerPartitionStreamSlice({}, {})), {}, id="test_cursor_slice_nested_empty_and_partition_mapping"),
        pytest.param(PerPartitionStreamSlice(PerPartitionStreamSlice({"partition": "value"}, {}), {}), {}, id="test_cursor_slice_nested_empty_and_partition"),
    ]
)
def test_cursor_slice(stream_slice, expected_cursor_slice):
    cursor_slice = stream_slice.cursor_slice

    assert cursor_slice == expected_cursor_slice
