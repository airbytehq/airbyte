#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class Hashabledict(dict):
    def __hash__(self):
        return hash(self._to_hashable(self))

    def _to_hashable(self, value):
        if type(value) == list:
            return (self._to_hashable(item) for item in value)
        elif type(value) in {dict, Hashabledict}:
            return frozenset(value), frozenset((self._to_hashable(item) for item in value.values()))
        return value


class PerPartitionStreamSlice(StreamSlice):
    def __init__(self, partition: Mapping[str, Any], cursor_slice: Mapping[str, Any]):
        self._partition = partition
        self._cursor_slice = cursor_slice
        self._stream_slice = partition | cursor_slice

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
        if type(other) == dict:
            return self._stream_slice == other
        if type(other) == PerPartitionStreamSlice:
            # noinspection PyProtectedMember
            return self._partition == other._partition and self._cursor_slice == other._cursor_slice
        return False

    def __ne__(self, other):
        return self.__eq__(other)


class PerPartitionCursor(StreamSlicer):
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

    def __init__(self, cursor_factory, partition_router):
        self._cursor_factory = cursor_factory
        self._partition_router = partition_router
        self._cursor_per_partition = {}
        self._default_cursor_state = self._NO_CURSOR_STATE

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[PerPartitionStreamSlice]:
        slices = self._partition_router.stream_slices(sync_mode, self._NO_STATE)
        for partition in slices:
            cursor = self._cursor_per_partition.get(self._to_tuple(partition))
            if not cursor:
                cursor = self._create_cursor(self._default_cursor_state)
                self._cursor_per_partition[self._to_tuple(partition)] = cursor

            for cursor_slice in cursor.stream_slices(sync_mode, self._get_state_for_partition(stream_state, partition)):
                yield PerPartitionStreamSlice(partition, cursor_slice)

    def update_cursor(self, stream_slice: PerPartitionStreamSlice, last_record: Optional[Record] = None):
        if not last_record:
            # The `update_cursor` method is called without `last_record` in order to set the initial state. In that case, stream_slice is
            # not a PerPartitionStreamSlice but is a dict representing the state
            self._init_state(stream_slice)
        else:
            try:
                self._cursor_per_partition[self._to_tuple(stream_slice.partition)].update_cursor(stream_slice.cursor_slice, last_record)
            except KeyError as exception:
                raise KeyError(
                    f"Partition {str(exception)} could not be found in current state based on the record. This is unexpected because "
                    f"we should only update cursor for partition that where emitted during `stream_slices`"
                )

    def _init_state(self, stream_slice: dict) -> None:
        for state in stream_slice["states"]:
            self._cursor_per_partition[self._to_tuple(state["partition"])] = self._create_cursor(state["cursor"])

    def set_default_state(self, default_state: dict) -> None:
        """
        Deprecated: this method only exist to support the migration of non per partition states
        """
        self._default_cursor_state = default_state

    def get_stream_state(self) -> StreamState:
        states = []
        for partition_tuple, cursor in self._cursor_per_partition.items():
            cursor_state = cursor.get_stream_state()
            if cursor_state:
                states.append(
                    {
                        "partition": self._to_dict(partition_tuple),
                        "cursor": cursor.get_stream_state(),
                    }
                )
        return {"states": states}

    def _get_state_for_partition(self, stream_state: StreamState, partition: StreamSlice) -> Any:
        if PerPartitionCursor._is_new_state(stream_state):
            return None
        if "states" not in stream_state:
            raise ValueError("Incompatible state format")

        for state in stream_state["states"]:
            if partition == state["partition"]:
                return state["cursor"]

        return self._default_cursor_state

    @staticmethod
    def _is_new_state(stream_state):
        return not bool(stream_state) or stream_state == {}

    @staticmethod
    def _to_tuple(partition) -> Tuple:
        return Hashabledict(partition)

    @staticmethod
    def _to_dict(partition_tuples: tuple) -> StreamSlice:
        return partition_tuples

    def select(
        self, stream_slice: Optional[PerPartitionStreamSlice] = None, stream_state: Optional[StreamState] = None
    ) -> Optional[StreamState]:
        if not stream_slice:
            raise ValueError("A partition needs to be provided in order to extract a state")

        if not stream_state:
            return None

        return self._get_state_for_partition(stream_state, stream_slice.partition)

    def _create_cursor(self, cursor_state: Any) -> StreamSlicer:
        cursor = self._cursor_factory.create()
        cursor.update_cursor(cursor_state)
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
        ) | self._cursor_per_partition[self._to_tuple(stream_slice.partition)].get_request_params(
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
        ) | self._cursor_per_partition[self._to_tuple(stream_slice.partition)].get_request_headers(
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
        ) | self._cursor_per_partition[self._to_tuple(stream_slice.partition)].get_request_body_data(
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
        ) | self._cursor_per_partition[self._to_tuple(stream_slice.partition)].get_request_body_json(
            stream_state=stream_state, stream_slice=stream_slice.cursor_slice, next_page_token=next_page_token
        )
