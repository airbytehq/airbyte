#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Generator, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


class GlobalParentCursor(DeclarativeCursor):
    """
    The GlobalParentCursor is designed to track the state of parent streams using a single global cursor.
    This class is useful for streams that have many partitions, allowing the state to be managed globally
    rather than per partition, which simplifies state management and reduces the size of state messages.

    This cursor will be used when the `global_parent_cursor` parameter is set for incremental sync.
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

        This method initializes the state for the global cursor using the provided stream state.
        If a partition state is provided in the stream state, it will update the corresponding global cursor with this state.

        Additionally, it sets the parent state for partition routers that are based on parent streams. If a partition router
        does not have parent streams, this step will be skipped due to the default PartitionRouter implementation.

        Args:
            stream_state (StreamState): The state of the streams to be set. The format of the stream state should be:
                {
                    "state": {
                        "last_updated": "2023-05-27T00:00:00Z"
                    },
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
        """
        Close the current stream slice.

        This method is called when a stream slice is completed. For the global parent cursor, we close the child cursor
        only after reading all slices. This ensures that we do not miss any child records from a later parent record
        if the child cursor is earlier than a record from the first parent record.

        Args:
            stream_slice (StreamSlice): The stream slice to be closed.
            *args (Any): Additional arguments.
        """
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
        return self._stream_cursor.is_greater_than_or_equal(
            self._convert_record_to_cursor_record(first), self._convert_record_to_cursor_record(second)
        )

    @staticmethod
    def _convert_record_to_cursor_record(record: Record) -> Record:
        return Record(
            record.data,
            StreamSlice(partition={}, cursor_slice=record.associated_slice.cursor_slice) if record.associated_slice else None,
        )
