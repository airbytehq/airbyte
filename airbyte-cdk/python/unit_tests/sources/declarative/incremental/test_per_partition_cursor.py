#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections import OrderedDict
from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import (
    PerPartitionCursor,
    PerPartitionKeySerializer,
    PerPartitionStreamSlice,
)
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record

PARTITION = {
    "partition_key string": "partition value",
    "partition_key int": 1,
    "partition_key list str": ["list item 1", "list item 2"],
    "partition_key list dict": [
        {
            "dict within list key 1-1": "dict within list value 1-1",
            "dict within list key 1-2": "dict within list value 1-2"
        },
        {"dict within list key 2": "dict within list value 2"},
    ],
    "partition_key nested dict": {
        "nested_partition_key 1": "a nested value",
        "nested_partition_key 2": "another nested value",
    },
}

CURSOR_SLICE_FIELD = "cursor slice field"
CURSOR_STATE_KEY = "cursor state"
CURSOR_STATE = {CURSOR_STATE_KEY: "a state value"}
NOT_CONSIDERED_BECAUSE_MOCKED_CURSOR_HAS_NO_STATE = "any"
STATE = {
    "states": [
        {
            "partition": {
                "partition_router_field_1": "X1",
                "partition_router_field_2": "Y1",
            },
            "cursor": {
                "cursor state field": 1
            }
        },
        {
            "partition": {
                "partition_router_field_1": "X2",
                "partition_router_field_2": "Y2",
            },
            "cursor": {
                "cursor state field": 2
            }
        },
    ]
}


def test_partition_serialization():
    serializer = PerPartitionKeySerializer()
    assert serializer.to_partition(serializer.to_partition_key(PARTITION)) == PARTITION


def test_partition_with_different_key_orders():
    ordered_dict = OrderedDict({"1": 1, "2": 2})
    same_dict_with_different_order = OrderedDict({"2": 2, "1": 1})
    serializer = PerPartitionKeySerializer()

    assert serializer.to_partition_key(ordered_dict) == serializer.to_partition_key(same_dict_with_different_order)


def test_given_tuples_in_json_then_deserialization_convert_to_list():
    """
    This is a known issue with the current implementation. However, the assumption is that this wouldn't be a problem as we only use the
    immutability and we expect stream slices to be immutable anyway
    """
    serializer = PerPartitionKeySerializer()
    partition_with_tuple = {"key": (1, 2, 3)}

    assert partition_with_tuple != serializer.to_partition(serializer.to_partition_key(partition_with_tuple))


def test_stream_slice_merge_dictionaries():
    stream_slice = PerPartitionStreamSlice({"partition key": "partition value"}, {"cursor key": "cursor value"})
    assert stream_slice == {"partition key": "partition value", "cursor key": "cursor value"}


def test_overlapping_slice_keys_raise_error():
    with pytest.raises(ValueError):
        PerPartitionStreamSlice({"overlapping key": "partition value"}, {"overlapping key": "cursor value"})


class MockedCursorBuilder:
    def __init__(self):
        self._stream_slices = []
        self._stream_state = {}

    def with_stream_slices(self, stream_slices):
        self._stream_slices = stream_slices
        return self

    def with_stream_state(self, stream_state):
        self._stream_state = stream_state
        return self

    def build(self):
        cursor = Mock(spec=Cursor)
        cursor.get_stream_state.return_value = self._stream_state
        cursor.stream_slices.return_value = self._stream_slices
        return cursor


@pytest.fixture()
def mocked_partition_router():
    return Mock(spec=StreamSlicer)


@pytest.fixture()
def mocked_cursor_factory():
    cursor_factory = Mock()
    cursor_factory.create.return_value = MockedCursorBuilder().build()
    return cursor_factory


def test_given_no_partition_when_stream_slices_then_no_slices(mocked_cursor_factory, mocked_partition_router):
    mocked_partition_router.stream_slices.return_value = []
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    slices = cursor.stream_slices()

    assert not next(slices, None)


def test_given_partition_router_without_state_has_one_partition_then_return_one_slice_per_cursor_slice(mocked_cursor_factory,
                                                                                                       mocked_partition_router):
    partition = {"partition_field_1": "a value", "partition_field_2": "another value"}
    mocked_partition_router.stream_slices.return_value = [partition]
    cursor_slices = [{"start_datetime": 1}, {"start_datetime": 2}]
    mocked_cursor_factory.create.return_value = MockedCursorBuilder().with_stream_slices(cursor_slices).build()
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    slices = cursor.stream_slices()

    assert list(slices) == [PerPartitionStreamSlice(partition, cursor_slice) for cursor_slice in cursor_slices]


def test_given_partition_associated_with_state_when_stream_slices_then_do_not_recreate_cursor(mocked_cursor_factory,
                                                                                              mocked_partition_router):
    partition = {"partition_field_1": "a value", "partition_field_2": "another value"}
    mocked_partition_router.stream_slices.return_value = [partition]
    cursor_slices = [{"start_datetime": 1}]
    mocked_cursor_factory.create.return_value = MockedCursorBuilder().with_stream_slices(cursor_slices).build()
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    cursor.set_initial_state({
        "states": [{
            "partition": partition,
            "cursor": CURSOR_STATE
        }]
    })
    mocked_cursor_factory.create.assert_called_once()
    slices = list(cursor.stream_slices())

    mocked_cursor_factory.create.assert_called_once()
    assert len(slices) == 1


def test_given_multiple_partitions_then_each_have_their_state(mocked_cursor_factory, mocked_partition_router):
    first_partition = {"first_partition_key": "first_partition_value"}
    mocked_partition_router.stream_slices.return_value = [
        first_partition,
        {"second_partition_key": "second_partition_value"}
    ]
    first_cursor = MockedCursorBuilder().with_stream_slices([{CURSOR_SLICE_FIELD: "first slice cursor value"}]).build()
    second_cursor = MockedCursorBuilder().with_stream_slices([{CURSOR_SLICE_FIELD: "second slice cursor value"}]).build()
    mocked_cursor_factory.create.side_effect = [first_cursor, second_cursor]
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    cursor.set_initial_state({
        "states": [{
            "partition": first_partition,
            "cursor": CURSOR_STATE
        }]
    })
    slices = list(cursor.stream_slices())

    first_cursor.stream_slices.assert_called_once()
    second_cursor.stream_slices.assert_called_once()
    assert slices == [
        PerPartitionStreamSlice(
            partition={"first_partition_key": "first_partition_value"},
            cursor_slice={CURSOR_SLICE_FIELD: "first slice cursor value"}
        ),
        PerPartitionStreamSlice(
            partition={"second_partition_key": "second_partition_value"},
            cursor_slice={CURSOR_SLICE_FIELD: "second slice cursor value"}
        ),
    ]


def test_given_stream_slices_when_get_stream_state_then_return_updated_state(mocked_cursor_factory, mocked_partition_router):
    mocked_cursor_factory.create.side_effect = [
        MockedCursorBuilder().with_stream_state({CURSOR_STATE_KEY: "first slice cursor value"}).build(),
        MockedCursorBuilder().with_stream_state({CURSOR_STATE_KEY: "second slice cursor value"}).build()
    ]
    mocked_partition_router.stream_slices.return_value = [{"partition key": "first partition"}, {"partition key": "second partition"}]
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)
    list(cursor.stream_slices())
    assert cursor.get_stream_state() == {
        "states": [
            {
                "partition": {"partition key": "first partition"},
                "cursor": {CURSOR_STATE_KEY: "first slice cursor value"}
            },
            {
                "partition": {"partition key": "second partition"},
                "cursor": {CURSOR_STATE_KEY: "second slice cursor value"}
            }
        ]
    }


def test_when_get_stream_state_then_delegate_to_underlying_cursor(mocked_cursor_factory, mocked_partition_router):
    underlying_cursor = MockedCursorBuilder().with_stream_slices([{CURSOR_SLICE_FIELD: "first slice cursor value"}]).build()
    mocked_cursor_factory.create.side_effect = [underlying_cursor]
    mocked_partition_router.stream_slices.return_value = [{"partition key": "first partition"}]
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)
    first_slice = list(cursor.stream_slices())[0]

    cursor.should_be_synced(
        Record(
            {},
            first_slice
        )
    )

    underlying_cursor.should_be_synced.assert_called_once_with(
        Record(
            {},
            first_slice.cursor_slice
        )
    )


def test_close_slice(mocked_cursor_factory, mocked_partition_router):
    underlying_cursor = MockedCursorBuilder().with_stream_slices([{CURSOR_SLICE_FIELD: "first slice cursor value"}]).build()
    mocked_cursor_factory.create.side_effect = [underlying_cursor]
    stream_slice = PerPartitionStreamSlice(partition={"partition key": "first partition"}, cursor_slice={})
    mocked_partition_router.stream_slices.return_value = [stream_slice.partition]
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)
    last_record = Mock()
    list(cursor.stream_slices())  # generate internal state

    cursor.close_slice(stream_slice, last_record)

    underlying_cursor.close_slice.assert_called_once_with(stream_slice.cursor_slice, Record(last_record.data, stream_slice.cursor_slice))


def test_given_no_last_record_when_close_slice_then_do_not_raise_error(mocked_cursor_factory, mocked_partition_router):
    underlying_cursor = MockedCursorBuilder().with_stream_slices([{CURSOR_SLICE_FIELD: "first slice cursor value"}]).build()
    mocked_cursor_factory.create.side_effect = [underlying_cursor]
    stream_slice = PerPartitionStreamSlice(partition={"partition key": "first partition"}, cursor_slice={})
    mocked_partition_router.stream_slices.return_value = [stream_slice.partition]
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)
    list(cursor.stream_slices())  # generate internal state

    cursor.close_slice(stream_slice, None)

    underlying_cursor.close_slice.assert_called_once_with(stream_slice.cursor_slice, None)


def test_given_unknown_partition_when_close_slice_then_raise_error():
    any_cursor_factory = Mock()
    any_partition_router = Mock()
    cursor = PerPartitionCursor(any_cursor_factory, any_partition_router)
    stream_slice = PerPartitionStreamSlice(partition={"unknown_partition": "unknown"}, cursor_slice={})
    with pytest.raises(ValueError):
        cursor.close_slice(
            stream_slice,
            Record({}, stream_slice)
        )


def test_given_unknown_partition_when_should_be_synced_then_raise_error():
    any_cursor_factory = Mock()
    any_partition_router = Mock()
    cursor = PerPartitionCursor(any_cursor_factory, any_partition_router)
    with pytest.raises(ValueError):
        cursor.should_be_synced(
            Record(
                {},
                PerPartitionStreamSlice(
                    partition={"unknown_partition": "unknown"},
                    cursor_slice={}
                )
            )
        )


def test_given_records_with_different_slice_when_is_greater_than_or_equal_then_raise_error():
    any_cursor_factory = Mock()
    any_partition_router = Mock()
    cursor = PerPartitionCursor(any_cursor_factory, any_partition_router)
    with pytest.raises(ValueError):
        cursor.is_greater_than_or_equal(
            Record({}, PerPartitionStreamSlice(partition={"a slice": "value"}, cursor_slice={})),
            Record({}, PerPartitionStreamSlice(partition={"another slice": "value"}, cursor_slice={}))
        )


def test_given_slice_is_unknown_when_is_greater_than_or_equal_then_raise_error():
    any_cursor_factory = Mock()
    any_partition_router = Mock()
    cursor = PerPartitionCursor(any_cursor_factory, any_partition_router)
    with pytest.raises(ValueError):
        cursor.is_greater_than_or_equal(
            Record({}, PerPartitionStreamSlice(partition={"a slice": "value"}, cursor_slice={})),
            Record({}, PerPartitionStreamSlice(partition={"a slice": "value"}, cursor_slice={}))
        )


def test_when_is_greater_than_or_equal_then_return_underlying_cursor_response(mocked_cursor_factory, mocked_partition_router):
    underlying_cursor = MockedCursorBuilder().with_stream_slices([{CURSOR_SLICE_FIELD: "first slice cursor value"}]).build()
    mocked_cursor_factory.create.side_effect = [underlying_cursor]
    stream_slice = PerPartitionStreamSlice(partition={"partition key": "first partition"}, cursor_slice={})
    mocked_partition_router.stream_slices.return_value = [stream_slice.partition]
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)
    first_record = Record({"first": "value"}, stream_slice)
    second_record = Record({"second": "value"}, stream_slice)
    list(cursor.stream_slices())  # generate internal state

    result = cursor.is_greater_than_or_equal(first_record, second_record)

    assert result == underlying_cursor.is_greater_than_or_equal.return_value
    underlying_cursor.is_greater_than_or_equal.assert_called_once_with(first_record, second_record)
