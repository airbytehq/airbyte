#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.incremental.global_substream_cursor import GlobalSubstreamCursor, iterate_with_last_flag
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import PerPartitionCursor, CursorFactory

from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


class PerPartitionWithGlobalCursor(DeclarativeCursor):
    """
    Manages state for streams with multiple partitions, with an optional fallback to a global cursor when specific conditions are met.

    This cursor is designed to handle cases where a stream is partitioned, allowing state management per partition. However, if a certain condition is met (e.g., the number of records in a partition exceeds 5 times a defined limit), the cursor will fallback to a global state.

    ## Overview

    Given a stream with many partitions, it is crucial to maintain a state per partition to avoid data loss or duplication. This class provides a mechanism to handle such cases and ensures that the stream's state is accurately maintained.

    ## State Management

    - **Partition-Based State**: Manages state individually for each partition, ensuring that each partition's data is processed correctly and independently.
    - **Global Fallback**: Switches to a global cursor when a predefined condition is met (e.g., the number of records in a partition exceeds a certain threshold). This ensures that the system can handle cases where partition-based state management is no longer efficient or viable.

    ## Example State Structure

    ```json
    {
        "states": [
            {"partition_key": "partition_1": "cursor_field": "2021-01-15"},
            {"partition_key": "partition_2": "cursor_field": "2021-02-14"}
        [,
        "state": {
            "cursor_field": "2021-02-15"
        },
        "use_global_cursor": false
    }
    ```
    """

    def __init__(self, cursor_factory: CursorFactory, partition_router: PartitionRouter, stream_cursor: DatetimeBasedCursor):
        self._partition_router = partition_router
        self._per_partition_cursor = PerPartitionCursor(cursor_factory, partition_router)
        self._global_cursor = GlobalSubstreamCursor(stream_cursor, partition_router)
        self._use_global_cursor = False

    def stream_slices(self) -> Iterable[StreamSlice]:
        self._global_cursor.start_slices_generation()

        # Iterate through partitions and process slices
        for partition, is_last_partition in iterate_with_last_flag(self._partition_router.stream_slices()):
            cursor = self._global_cursor if self._use_global_cursor else self._per_partition_cursor
            # Generate slices for the current cursor and handle the last slice using the flag
            for slice, is_last_slice in iterate_with_last_flag(
                    cursor.generate_slices_from_partition(partition=partition)):
                self._global_cursor.register_slice(is_last_slice and is_last_partition)
                yield slice

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state for the cursors.
        """
        self._use_global_cursor = stream_state.get("use_global_cursor", False)

        self._global_cursor.set_initial_state(stream_state)
        self._per_partition_cursor.set_initial_state(stream_state)

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        if not self._use_global_cursor and self._per_partition_cursor.limit_reached():
            self._use_global_cursor = True

        if not self._use_global_cursor:
            self._per_partition_cursor.observe(stream_slice, record)
        self._global_cursor.observe(stream_slice, record)

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        if not self._use_global_cursor:
            self._per_partition_cursor.close_slice(stream_slice, *args)
        self._global_cursor.close_slice(stream_slice, *args)

    def get_stream_state(self) -> StreamState:
        final_state = {"use_global_cursor": self._use_global_cursor}

        final_state.update(self._global_cursor.get_stream_state())
        if not self._use_global_cursor:
            final_state.update(self._per_partition_cursor.get_stream_state())

        return final_state

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        if self._use_global_cursor:
            return self._global_cursor.select_state(stream_slice)
        else:
            return self._per_partition_cursor.select_state(stream_slice)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if self._use_global_cursor:
            return self._global_cursor.get_request_params(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )
        else:
            return self._per_partition_cursor.get_request_params(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if self._use_global_cursor:
            return self._global_cursor.get_request_headers(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )
        else:
            return self._per_partition_cursor.get_request_headers(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        if self._use_global_cursor:
            return self._global_cursor.get_request_body_data(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )
        else:
            return self._per_partition_cursor.get_request_body_data(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )


    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        if self._use_global_cursor:
            return self._global_cursor.get_request_body_json(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )
        else:
            return self._per_partition_cursor.get_request_body_json(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )

    def should_be_synced(self, record: Record) -> bool:
        return self._global_cursor.should_be_synced(record) or self._per_partition_cursor.should_be_synced(record)

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        return self._global_cursor.is_greater_than_or_equal(first, second)
