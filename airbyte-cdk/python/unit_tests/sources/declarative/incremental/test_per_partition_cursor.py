#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import PerPartitionCursor, PerPartitionStreamSlice
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer

CURSOR_SLICE_FIELD = "cursor slice field"
CURSOR_STATE_KEY = "cursor state"
CURSOR_STATE = {CURSOR_STATE_KEY: "a state value"}
NOT_CONSIDERED_BECAUSE_MOCKED_CURSOR_HAS_NO_STATE = "any"
SYNC_MODE = SyncMode.full_refresh
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
        cursor = Mock(spec=StreamSlicer)
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

    slices = cursor.stream_slices(SYNC_MODE, STATE)

    assert not next(slices, None)


def test_given_partition_router_without_state_has_one_partition_then_return_one_slice_per_cursor_slice(mocked_cursor_factory, mocked_partition_router):
    partition = {"partition_field_1": "a value", "partition_field_2": "another value"}
    mocked_partition_router.stream_slices.return_value = [partition]
    cursor_slices = [{"start_datetime": 1}, {"start_datetime": 2}]
    mocked_cursor_factory.create.return_value = MockedCursorBuilder().with_stream_slices(cursor_slices).build()
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    slices = cursor.stream_slices(SYNC_MODE, STATE)

    assert list(slices) == [PerPartitionStreamSlice(partition, cursor_slice) for cursor_slice in cursor_slices]


def test_given_previous_state_format_when_update_cursor_then_raise_error(mocked_cursor_factory, mocked_partition_router):
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    with pytest.raises(ValueError):
        cursor.update_cursor({"start_datetime": "2022-08-18T08:35:49.540Z"})


def test_given_partition_associated_with_state_when_stream_slices_then_do_not_recreate_cursor(mocked_cursor_factory, mocked_partition_router):
    partition = {"partition_field_1": "a value", "partition_field_2": "another value"}
    mocked_partition_router.stream_slices.return_value = [partition]
    cursor_slices = [{"start_datetime": 1}]
    mocked_cursor_factory.create.return_value = MockedCursorBuilder().with_stream_slices(cursor_slices).build()
    cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)

    cursor.update_cursor({
        "states": [{
            "partition": partition,
            "cursor": CURSOR_STATE
        }]
    })
    mocked_cursor_factory.create.assert_called_once()
    slices = list(cursor.stream_slices(SYNC_MODE, STATE))

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

    cursor.update_cursor({
        "states": [{
            "partition": first_partition,
            "cursor": CURSOR_STATE
        }]
    })
    slices = list(cursor.stream_slices(SYNC_MODE, STATE))

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
    list(cursor.stream_slices(SYNC_MODE, {}))
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


def test_state_retrieval():
    cursor = PerPartitionCursor(None, None)
    state_for_partition = cursor._get_state_for_partition(STATE, {"partition_router_field_1": "X1", "partition_router_field_2": "Y1"})
    assert state_for_partition == {"cursor state field": 1}
