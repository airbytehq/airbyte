#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.incremental.global_substream_cursor import GlobalSubstreamCursor, iterate_with_last_flag_and_state
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import CursorFactory, PerPartitionCursor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


class PerPartitionWithGlobalCursor(DeclarativeCursor):
    """
    Manages state for streams with multiple partitions, with an optional fallback to a global cursor when specific conditions are met.

    This cursor handles partitioned streams by maintaining individual state per partition using `PerPartitionCursor`. If the number of partitions exceeds a defined limit, it switches to a global cursor (`GlobalSubstreamCursor`) to manage state more efficiently.

    **Overview**

    - **Partition-Based State**: Initially manages state per partition to ensure accurate processing of each partition's data.
    - **Global Fallback**: Switches to a global cursor when the partition limit is exceeded to handle state management more effectively.

    **Switching Logic**

    - Monitors the number of partitions.
    - If `PerPartitionCursor.limit_reached()` returns `True`, sets `_use_global_cursor` to `True`, activating the global cursor.

    **Active Cursor Selection**

    - Uses the `_get_active_cursor()` helper method to select the active cursor based on the `_use_global_cursor` flag.
    - This simplifies the logic and ensures consistent cursor usage across methods.

    **State Structure Example**

    ```json
    {
        "states": [
            {
                "partition": {"partition_key": "partition_1"},
                "cursor": {"cursor_field": "2021-01-15"}
            },
            {
                "partition": {"partition_key": "partition_2"},
                "cursor": {"cursor_field": "2021-02-14"}
            }
        ],
        "state": {
            "cursor_field": "2021-02-15"
        },
        "use_global_cursor": false
    }
    ```

    In this example, the cursor is using partition-based state management (`"use_global_cursor": false`), maintaining separate cursor states for each partition.

    **Usage Scenario**

    Suitable for streams where the number of partitions may vary significantly, requiring dynamic switching between per-partition and global state management to ensure data consistency and efficient synchronization.
    """

    def __init__(self, cursor_factory: CursorFactory, partition_router: PartitionRouter, stream_cursor: DatetimeBasedCursor):
        self._partition_router = partition_router
        self._per_partition_cursor = PerPartitionCursor(cursor_factory, partition_router)
        self._global_cursor = GlobalSubstreamCursor(stream_cursor, partition_router)
        self._use_global_cursor = False
        self._current_partition: Optional[Mapping[str, Any]] = None
        self._last_slice: bool = False
        self._parent_state: Optional[Mapping[str, Any]] = None

    def _get_active_cursor(self) -> Union[PerPartitionCursor, GlobalSubstreamCursor]:
        return self._global_cursor if self._use_global_cursor else self._per_partition_cursor

    def stream_slices(self) -> Iterable[StreamSlice]:
        self._global_cursor.start_slices_generation()

        # Iterate through partitions and process slices
        for partition, is_last_partition, parent_state in iterate_with_last_flag_and_state(
            self._partition_router.stream_slices(), self._partition_router.get_stream_state
        ):
            # Generate slices for the current cursor and handle the last slice using the flag
            self._parent_state = parent_state
            for slice, is_last_slice, _ in iterate_with_last_flag_and_state(
                self._get_active_cursor().generate_slices_from_partition(partition=partition), lambda: None
            ):
                self._global_cursor.register_slice(is_last_slice and is_last_partition)
                yield slice
        self._parent_state = self._partition_router.get_stream_state()

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state for the cursors.
        """
        self._use_global_cursor = stream_state.get("use_global_cursor", False)

        self._parent_state = stream_state.get("parent_state", {})

        self._global_cursor.set_initial_state(stream_state)
        if not self._use_global_cursor:
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
        final_state: MutableMapping[str, Any] = {"use_global_cursor": self._use_global_cursor}

        final_state.update(self._global_cursor.get_stream_state())
        if not self._use_global_cursor:
            final_state.update(self._per_partition_cursor.get_stream_state())

        final_state["parent_state"] = self._parent_state
        if not final_state.get("parent_state"):
            del final_state["parent_state"]

        return final_state

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        return self._get_active_cursor().select_state(stream_slice)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_active_cursor().get_request_params(
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
        return self._get_active_cursor().get_request_headers(
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
        return self._get_active_cursor().get_request_body_data(
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
        return self._get_active_cursor().get_request_body_json(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

    def should_be_synced(self, record: Record) -> bool:
        return self._global_cursor.should_be_synced(record) or self._per_partition_cursor.should_be_synced(record)

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        return self._global_cursor.is_greater_than_or_equal(first, second)
