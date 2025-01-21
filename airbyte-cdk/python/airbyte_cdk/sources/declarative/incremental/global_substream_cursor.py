#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import threading
import time
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


class Timer:
    """
    A simple timer class that measures elapsed time in seconds using a high-resolution performance counter.
    """

    def __init__(self) -> None:
        self._start: Optional[int] = None

    def start(self) -> None:
        self._start = time.perf_counter_ns()

    def finish(self) -> int:
        if self._start:
            return int((time.perf_counter_ns() - self._start) // 1e9)
        else:
            raise RuntimeError("Global substream cursor timer not started")


class GlobalSubstreamCursor(DeclarativeCursor):
    """
    The GlobalSubstreamCursor is designed to track the state of substreams using a single global cursor.
    This class is beneficial for streams with many partitions, as it allows the state to be managed globally
    instead of per partition, simplifying state management and reducing the size of state messages.

    This cursor is activated by setting the `global_substream_cursor` parameter for incremental sync.

    Warnings:
    - This class enforces a minimal lookback window for substream based on the duration of the previous sync to avoid losing records. This lookback ensures that any records added or updated during the sync are captured in subsequent syncs.
    - The global cursor is updated only at the end of the sync. If the sync ends prematurely (e.g., due to an exception), the state will not be updated.
    - When using the `incremental_dependency` option, the sync will progress through parent records, preventing the sync from getting infinitely stuck. However, it is crucial to understand the requirements for both the `global_substream_cursor` and `incremental_dependency` options to avoid data loss.
    """

    def __init__(self, stream_cursor: DatetimeBasedCursor, partition_router: PartitionRouter):
        self._stream_cursor = stream_cursor
        self._partition_router = partition_router
        self._timer = Timer()
        self._lock = threading.Lock()
        self._slice_semaphore = threading.Semaphore(0)  # Start with 0, indicating no slices being tracked
        self._all_slices_yielded = False
        self._lookback_window: Optional[int] = None

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Generates stream slices, ensuring the last slice is properly flagged and processed.

        This method creates a sequence of stream slices by iterating over partitions and cursor slices.
        It holds onto one slice in memory to set `_all_slices_yielded` to `True` before yielding the
        final slice. A semaphore is used to track the processing of slices, ensuring that `close_slice`
        is called only after all slices have been processed.

        We expect the following events:
        * Yields all the slices except the last one. At this point, `close_slice` won't actually close the global slice as `self._all_slices_yielded == False`
        * Release the semaphore one last time before setting `self._all_slices_yielded = True`. This will cause `close_slice` to know about all the slices before we indicate that all slices have been yielded so the left side of `if self._all_slices_yielded and self._slice_semaphore._value == 0` will be false if not everything is closed
        * Setting `self._all_slices_yielded = True`. We do that before actually yielding the last slice as the caller of `stream_slices` might stop iterating at any point and hence the code after `yield` might not be executed
        * Yield the last slice. At that point, once there are as many slices yielded as closes, the global slice will be closed too
        """
        previous_slice = None

        slice_generator = (
            StreamSlice(partition=partition, cursor_slice=cursor_slice)
            for partition in self._partition_router.stream_slices()
            for cursor_slice in self._stream_cursor.stream_slices()
        )
        self._timer.start()

        for slice in slice_generator:
            if previous_slice is not None:
                # Release the semaphore to indicate that a slice has been yielded
                self._slice_semaphore.release()
                yield previous_slice

            # Store the current slice as the previous slice for the next iteration
            previous_slice = slice

        # After all slices have been generated, release the semaphore one final time
        # and flag that all slices have been yielded
        self._slice_semaphore.release()
        self._all_slices_yielded = True

        # Yield the last slice
        if previous_slice is not None:
            yield previous_slice

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state for the cursors.

        This method initializes the state for the global cursor using the provided stream state.

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
                    },
                    "lookback_window": 132
                }
        """
        if not stream_state:
            return

        if "lookback_window" in stream_state:
            self._lookback_window = stream_state["lookback_window"]
            self._inject_lookback_into_stream_cursor(stream_state["lookback_window"])

        self._stream_cursor.set_initial_state(stream_state["state"])

        # Set parent state for partition routers based on parent streams
        self._partition_router.set_initial_state(stream_state)

    def _inject_lookback_into_stream_cursor(self, lookback_window: int) -> None:
        """
        Modifies the stream cursor's lookback window based on the duration of the previous sync.
        This adjustment ensures the cursor is set to the minimal lookback window necessary for
        avoiding missing data.

        Parameters:
            lookback_window (int): The lookback duration in seconds to be set, derived from
                                   the previous sync.

        Raises:
            ValueError: If the cursor does not support dynamic lookback window adjustments.
        """
        if hasattr(self._stream_cursor, "set_runtime_lookback_window"):
            self._stream_cursor.set_runtime_lookback_window(lookback_window)
        else:
            raise ValueError("The cursor class for Global Substream Cursor does not have a set_runtime_lookback_window method")

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
        with self._lock:
            self._slice_semaphore.acquire()
            if self._all_slices_yielded and self._slice_semaphore._value == 0:
                self._lookback_window = self._timer.finish()
                self._stream_cursor.close_slice(StreamSlice(partition={}, cursor_slice=stream_slice.cursor_slice), *args)

    def get_stream_state(self) -> StreamState:
        state: dict[str, Any] = {"state": self._stream_cursor.get_stream_state()}

        parent_state = self._partition_router.get_stream_state()
        if parent_state:
            state["parent_state"] = parent_state

        if self._lookback_window is not None:
            state["lookback_window"] = self._lookback_window

        return state

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        # stream_slice is ignored as cursor is global
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
