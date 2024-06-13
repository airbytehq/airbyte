#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


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
    def to_partition(to_deserialize: Any) -> Mapping[str, Any]:
        return json.loads(to_deserialize)  # type: ignore # The partition is known to be a dict, but the type hint is Any


class CursorFactory:
    def __init__(self, create_function: Callable[[], DeclarativeCursor]):
        self._create_function = create_function

    def create(self) -> DeclarativeCursor:
        return self._create_function()


class PerPartitionCursor(DeclarativeCursor):
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

    _NO_STATE: Mapping[str, Any] = {}
    _NO_CURSOR_STATE: Mapping[str, Any] = {}
    _KEY = 0
    _VALUE = 1

    def __init__(self, cursor_factory: CursorFactory, partition_router: PartitionRouter):
        self._cursor_factory = cursor_factory
        self._partition_router = partition_router
        self._cursor_per_partition: MutableMapping[str, DeclarativeCursor] = {}
        self._partition_serializer = PerPartitionKeySerializer()

    def stream_slices(self) -> Iterable[StreamSlice]:
        slices = self._partition_router.stream_slices()
        for partition in slices:
            cursor = self._cursor_per_partition.get(self._to_partition_key(partition.partition))
            if not cursor:
                cursor = self._create_cursor(self._NO_CURSOR_STATE)
                self._cursor_per_partition[self._to_partition_key(partition.partition)] = cursor

            for cursor_slice in cursor.stream_slices():
                yield StreamSlice(partition=partition, cursor_slice=cursor_slice)

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state for the cursors.

        This method initializes the state for each partition cursor using the provided stream state.
        If a partition state is provided in the stream state, it will update the corresponding partition cursor with this state.

        Additionally, it sets the parent state for partition routers that are based on parent streams. If a partition router
        does not have parent streams, this step will be skipped due to the default PartitionRouter implementation.

        Args:
            stream_state (StreamState): The state of the streams to be set. The format of the stream state should be:
                {
                    "states": [
                        {
                            "partition": {
                                "partition_key": "value"
                            },
                            "cursor": {
                                "last_updated": "2023-05-27T00:00:00Z"
                            }
                        }
                    ],
                    "parent_state": {
                        "parent_stream_name": {
                            "last_updated": "2023-05-27T00:00:00Z"
                        }
                    }
                }
        """
        if not stream_state:
            return

        for state in stream_state["states"]:
            self._cursor_per_partition[self._to_partition_key(state["partition"])] = self._create_cursor(state["cursor"])

        # Set parent state for partition routers based on parent streams
        self._partition_router.set_initial_state(stream_state)

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].observe(
            StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice), record
        )

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        try:
            self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].close_slice(
                StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice), *args
            )
        except KeyError as exception:
            raise ValueError(
                f"Partition {str(exception)} could not be found in current state based on the record. This is unexpected because "
                f"we should only update state for partitions that were emitted during `stream_slices`"
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
        state: dict[str, Any] = {"states": states}

        parent_state = self._partition_router.get_stream_state()
        if parent_state:
            state["parent_state"] = parent_state
        return state

    def _get_state_for_partition(self, partition: Mapping[str, Any]) -> Optional[StreamState]:
        cursor = self._cursor_per_partition.get(self._to_partition_key(partition))
        if cursor:
            return cursor.get_stream_state()

        return None

    @staticmethod
    def _is_new_state(stream_state: Mapping[str, Any]) -> bool:
        return not bool(stream_state)

    def _to_partition_key(self, partition: Mapping[str, Any]) -> str:
        return self._partition_serializer.to_partition_key(partition)

    def _to_dict(self, partition_key: str) -> Mapping[str, Any]:
        return self._partition_serializer.to_partition(partition_key)

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        if not stream_slice:
            raise ValueError("A partition needs to be provided in order to extract a state")

        if not stream_slice:
            return None

        return self._get_state_for_partition(stream_slice.partition)

    def _create_cursor(self, cursor_state: Any) -> DeclarativeCursor:
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
        if stream_slice:
            return self._partition_router.get_request_params(  # type: ignore # this always returns a mapping
                stream_state=stream_state,
                stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={}),
                next_page_token=next_page_token,
            ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_params(
                stream_state=stream_state,
                stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice),
                next_page_token=next_page_token,
            )
        else:
            raise ValueError("A partition needs to be provided in order to get request params")

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if stream_slice:
            return self._partition_router.get_request_headers(  # type: ignore # this always returns a mapping
                stream_state=stream_state,
                stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={}),
                next_page_token=next_page_token,
            ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_headers(
                stream_state=stream_state,
                stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice),
                next_page_token=next_page_token,
            )
        else:
            raise ValueError("A partition needs to be provided in order to get request headers")

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        if stream_slice:
            return self._partition_router.get_request_body_data(  # type: ignore # this always returns a mapping
                stream_state=stream_state,
                stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={}),
                next_page_token=next_page_token,
            ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_body_data(
                stream_state=stream_state,
                stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice),
                next_page_token=next_page_token,
            )
        else:
            raise ValueError("A partition needs to be provided in order to get request body data")

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if stream_slice:
            return self._partition_router.get_request_body_json(  # type: ignore # this always returns a mapping
                stream_state=stream_state,
                stream_slice=StreamSlice(partition=stream_slice.partition, cursor_slice={}),
                next_page_token=next_page_token,
            ) | self._cursor_per_partition[self._to_partition_key(stream_slice.partition)].get_request_body_json(
                stream_state=stream_state,
                stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice),
                next_page_token=next_page_token,
            )
        else:
            raise ValueError("A partition needs to be provided in order to get request body json")

    def should_be_synced(self, record: Record) -> bool:
        return self._get_cursor(record).should_be_synced(self._convert_record_to_cursor_record(record))

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        if not first.associated_slice or not second.associated_slice:
            raise ValueError(f"Both records should have an associated slice but got {first.associated_slice} and {second.associated_slice}")
        if first.associated_slice.partition != second.associated_slice.partition:
            raise ValueError(
                f"To compare records, partition should be the same but got {first.associated_slice.partition} and {second.associated_slice.partition}"
            )

        return self._get_cursor(first).is_greater_than_or_equal(
            self._convert_record_to_cursor_record(first), self._convert_record_to_cursor_record(second)
        )

    @staticmethod
    def _convert_record_to_cursor_record(record: Record) -> Record:
        return Record(
            record.data,
            StreamSlice(partition={}, cursor_slice=record.associated_slice.cursor_slice) if record.associated_slice else None,
        )

    def _get_cursor(self, record: Record) -> DeclarativeCursor:
        if not record.associated_slice:
            raise ValueError("Invalid state as stream slices that are emitted should refer to an existing cursor")
        partition_key = self._to_partition_key(record.associated_slice.partition)
        if partition_key not in self._cursor_per_partition:
            raise ValueError("Invalid state as stream slices that are emitted should refer to an existing cursor")
        cursor = self._cursor_per_partition[partition_key]
        return cursor
