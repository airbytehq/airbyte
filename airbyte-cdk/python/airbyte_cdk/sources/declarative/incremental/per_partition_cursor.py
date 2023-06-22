#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Callable, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class PerPartitionKeySerializer:
    """
    We are concerned of the performance of looping through the `states` list and evaluating equality on the partition. To reduce this
    concern, we wanted to use dictionaries to map `partition -> cursor`. However, partitions are dict and dict can't be used as dict keys
    since they are not hashable. By creating json string using the dict, we can have a use the dict as a key to the dict since strings are
    hashable.
    """

    @staticmethod
    def to_partition_key(to_serialize: Any) -> str:
        # separators have changed in Python 3.4. To avoid being impacted by further change, we explicitly specify our own value
        return json.dumps(to_serialize, indent=None, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def to_partition(to_deserialize: Any):
        return json.loads(to_deserialize)


class PerPartitionStreamSlice(StreamSlice):
    def __init__(self, partition: Mapping[str, Any], cursor_slice: Mapping[str, Any]):
        self._partition = partition
        self._cursor_slice = cursor_slice
        if partition.keys() & cursor_slice.keys():
            raise ValueError("Keys for partition and incremental sync cursor should not overlap")
        self._stream_slice = dict(partition) | dict(cursor_slice)

    @property
    def partition(self):
        return self._partition

    @property
    def cursor_slice(self):
        return self._cursor_slice

    def __repr__(self):
        return repr(self._stream_slice)

    def __setitem__(self, key: str, value: Any):
        raise ValueError("PerPartitionStreamSlice is immutable")

    def __getitem__(self, key: str):
        return self._stream_slice[key]

    def __len__(self):
        return len(self._stream_slice)

    def __iter__(self):
        return iter(self._stream_slice)

    def __contains__(self, item: str):
        return item in self._stream_slice

    def keys(self):
        return self._stream_slice.keys()

    def items(self):
        return self._stream_slice.items()

    def values(self):
        return self._stream_slice.values()

    def get(self, key: str, default: Any) -> Any:
        return self._stream_slice.get(key, default)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._stream_slice == other
        if isinstance(other, PerPartitionStreamSlice):
            # noinspection PyProtectedMember
            return self._partition == other._partition and self._cursor_slice == other._cursor_slice
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class CursorFactory:
    def __init__(self, create_function: Callable[[], StreamSlicer]):
        self._create_function = create_function

    def create(self) -> StreamSlicer:
        return self._create_function()


class PerPartitionCursor(Cursor):
    """
    Given a stream has many partitions, it is important to provide a state per partition.

    Record | Stream Slice | Last Record | DatetimeCursorBased cursor
    -- | -- | -- | --
    1 | {"start_time": "2021-01-01","end_time": "2021-01-31","owner_resource": "1"''} | cursor_field: “2021-01-15” | 2021-01-15
    2 | {"start_time": "2021-02-01","end_time": "2021-02-28","owner_resource": "1"''} | cursor_field: “2021-02-15” | 2021-02-15
    3 | {"start_time": "2021-01-01","end_time": "2021-01-31","owner_resource": "2"''} | cursor_field: “2021-01-03” | 2021-01-03
    4 | {"start_time": "2021-02-01","end_time": "2021-02-28","owner_resource": "2"''} | cursor_field: “2021-02-14” | 2021-02-14

    Given the following errors, this can lead to some loss or duplication of records:
    When | Problem | Affected Record
    -- | -- | --
    Between record #1 and #2 | Loss | #3
    Between record #2 and #3 | Loss | #3, #4
    Between record #3 and #4 | Duplication | #1, #2

    Therefore, we need to manage state per partition.
    """

    _NO_STATE = {}
    _NO_CURSOR_STATE = {}
    _KEY = 0
    _VALUE = 1

    def __init__(self, cursor_factory: CursorFactory, partition_router: StreamSlicer):
        self._cursor_factory = cursor_factory
        self._partition_router = partition_router
        self._cursor_per_partition = {}
        self._partition_serializer = PerPartitionKeySerializer()

    def stream_slices(self) -> Iterable[PerPartitionStreamSlice]:
        slices = self._partition_router.stream_slices()
        for partition in slices:
            cursor = self._cursor_per_partition.get(self._to_partition_key(partition))
            if not cursor:
                cursor = self._create_cursor(self._NO_CURSOR_STATE)
                self._cursor_per_partition[self._to_partition_key(partition)] = cursor

            for cursor_slice in cursor.stream_slices():
                yield PerPartitionStreamSlice(partition, cursor_slice)

    def set_initial_state(self, stream_state: StreamState) -> None:
        if not stream_state:
            return

        for state in stream_state["states"]:
            self._cursor_per_partition[self._to_partition_key(state["partition"])] = self._create_cursor(state["cursor"])

    def update_state(self, stream_slice: PerPartitionStreamSlice, last_record: Record):
        try:
            self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].update_state(stream_slice.cursor_slice, last_record)
        except KeyError as exception:
            raise KeyError(
                f"Partition {str(exception)} could not be found in current state based on the record. This is unexpected because "
                f"we should only update state for partition that where emitted during `stream_slices`"
            )

    def get_stream_state(self) -> StreamState:
        states = []
        for partition_tuple, cursor in self._cursor_per_partition.items():
            cursor_state = cursor.get_stream_state()
            if cursor_state:
                states.append(
                    {
                        "partition": self._to_dict(partition_tuple),
                        "cursor": cursor_state,
                    }
                )
        return {"states": states}

    def _get_state_for_partition(self, partition: Mapping[str, Any]) -> Optional[StreamState]:
        cursor = self._cursor_per_partition.get(self._to_partition_key(partition))
        if cursor:
            return cursor.get_stream_state()

        return None

    @staticmethod
    def _is_new_state(stream_state):
        return not bool(stream_state)

    def _to_partition_key(self, partition) -> tuple:
        return self._partition_serializer.to_partition_key(partition)

    def _to_dict(self, partition_key: tuple) -> StreamSlice:
        return self._partition_serializer.to_partition(partition_key)

    def select_state(self, stream_slice: Optional[PerPartitionStreamSlice] = None) -> Optional[StreamState]:
        if not stream_slice:
            raise ValueError("A partition needs to be provided in order to extract a state")

        if not stream_slice:
            return None

        return self._get_state_for_partition(stream_slice.partition)

    def _create_cursor(self, cursor_state: Any) -> StreamSlicer:
        cursor = self._cursor_factory.create()
        cursor.set_initial_state(cursor_state)
        return cursor

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_params(
            stream_state=stream_state, stream_slice=stream_slice.partition, next_page_token=next_page_token
        ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_params(
            stream_state=stream_state, stream_slice=stream_slice.cursor_slice, next_page_token=next_page_token
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_headers(
            stream_state=stream_state, stream_slice=stream_slice.partition, next_page_token=next_page_token
        ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_headers(
            stream_state=stream_state, stream_slice=stream_slice.cursor_slice, next_page_token=next_page_token
        )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_body_data(
            stream_state=stream_state, stream_slice=stream_slice.partition, next_page_token=next_page_token
        ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_body_data(
            stream_state=stream_state, stream_slice=stream_slice.cursor_slice, next_page_token=next_page_token
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._partition_router.get_request_body_json(
            stream_state=stream_state, stream_slice=stream_slice.partition, next_page_token=next_page_token
        ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_body_json(
            stream_state=stream_state, stream_slice=stream_slice.cursor_slice, next_page_token=next_page_token
        )
