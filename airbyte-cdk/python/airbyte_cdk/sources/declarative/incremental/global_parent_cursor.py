#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Generator, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


class GlobalParentCursor(DeclarativeCursor):
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

    def __init__(self, stream_cursor: DeclarativeCursor, partition_router: PartitionRouter):
        self._stream_cursor = stream_cursor
        self._partition_router = partition_router

    def stream_slices(self) -> Iterable[StreamSlice]:
        def flag_last(generator: Generator[StreamSlice, None, None]) -> Generator[StreamSlice, None, None]:
            previous = None
            for item in generator:
                if previous is not None:
                    yield previous
                previous = item
            if previous is not None:
                yield StreamSlice(partition=previous.partition, cursor_slice=previous.cursor_slice, last_slice=True)

        slices = (
            StreamSlice(partition=partition, cursor_slice=cursor_slice)
            for partition in self._partition_router.stream_slices()
            for cursor_slice in self._stream_cursor.stream_slices()
        )

        yield from flag_last(slices)

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

        self._stream_cursor.set_initial_state(stream_state["state"])

        # Set parent state for partition routers based on parent streams
        self._partition_router.set_initial_state(stream_state)

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        self._stream_cursor.observe(StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice), record)

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        if stream_slice.last_slice:
            self._stream_cursor.close_slice(StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice), *args)

    def get_stream_state(self) -> StreamState:
        state: dict[str, Any] = {"state": self._stream_cursor.get_stream_state()}

        parent_state = self._partition_router.get_stream_state()
        if parent_state:
            state["parent_state"] = parent_state

        return state

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        return self._stream_cursor.get_stream_state()

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
            ) | self._stream_cursor.get_request_params(
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
            ) | self._stream_cursor.get_request_headers(
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
            ) | self._stream_cursor.get_request_body_data(
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
            ) | self._stream_cursor.get_request_body_json(
                stream_state=stream_state,
                stream_slice=StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice),
                next_page_token=next_page_token,
            )
        else:
            raise ValueError("A partition needs to be provided in order to get request body json")

    def should_be_synced(self, record: Record) -> bool:
        return self._stream_cursor.should_be_synced(self._convert_record_to_cursor_record(record))

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        # if not first.associated_slice or not second.associated_slice:
        #     raise ValueError(f"Both records should have an associated slice but got {first.associated_slice} and {second.associated_slice}")
        # if first.associated_slice.partition != second.associated_slice.partition:
        #     raise ValueError(
        #         f"To compare records, partition should be the same but got {first.associated_slice.partition} and {second.associated_slice.partition}"
        #     )

        return self._stream_cursor.is_greater_than_or_equal(
            self._convert_record_to_cursor_record(first), self._convert_record_to_cursor_record(second)
        )

    @staticmethod
    def _convert_record_to_cursor_record(record: Record) -> Record:
        return Record(
            record.data,
            StreamSlice(partition={}, cursor_slice=record.associated_slice.cursor_slice) if record.associated_slice else None,
        )
