# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.types import StreamSlice

from .cursor import Cursor


class CheckpointMode(Enum):
    INCREMENTAL = "incremental"
    RESUMABLE_FULL_REFRESH = "resumable_full_refresh"
    FULL_REFRESH = "full_refresh"


class CheckpointReader(ABC):
    """
    CheckpointReader manages how to iterate over a stream's partitions and serves as the bridge for interpreting the current state
    of the stream that should be emitted back to the platform.
    """

    @abstractmethod
    def next(self) -> Optional[Mapping[str, Any]]:
        """
        Returns the next slice that will be used to fetch the next group of records. Returning None indicates that the reader
        has finished iterating over all slices.
        """

    @abstractmethod
    def observe(self, new_state: Mapping[str, Any]) -> None:
        """
        Updates the internal state of the checkpoint reader based on the incoming stream state from a connector.

        WARNING: This is used to retain backwards compatibility with streams using the legacy get_stream_state() method.
        In order to uptake Resumable Full Refresh, connectors must migrate streams to use the state setter/getter methods.
        """

    @abstractmethod
    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        """
        Retrieves the current state value of the stream. The connector does not emit state messages if the checkpoint value is None.
        """


class IncrementalCheckpointReader(CheckpointReader):
    """
    IncrementalCheckpointReader handles iterating through a stream based on partitioned windows of data that are determined
    before syncing data.
    """

    def __init__(self, stream_state: Mapping[str, Any], stream_slices: Iterable[Optional[Mapping[str, Any]]]):
        self._state: Optional[Mapping[str, Any]] = stream_state
        self._stream_slices = iter(stream_slices)
        self._has_slices = False

    def next(self) -> Optional[Mapping[str, Any]]:
        try:
            next_slice = next(self._stream_slices)
            self._has_slices = True
            return next_slice
        except StopIteration:
            # This is used to avoid sending a duplicate state message at the end of a sync since the stream has already
            # emitted state at the end of each slice. If we want to avoid this extra complexity, we can also just accept
            # that every sync emits a final duplicate state
            if self._has_slices:
                self._state = None
            return None

    def observe(self, new_state: Mapping[str, Any]) -> None:
        self._state = new_state

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return self._state


class CursorBasedCheckpointReader(CheckpointReader):
    """
    CursorBasedCheckpointReader is used by streams that implement a Cursor in order to manage state. This allows the checkpoint
    reader to delegate the complexity of fetching state to the cursor and focus on the iteration over a stream's partitions.

    This reader supports the Cursor interface used by Python and low-code sources. Not to be confused with Cursor interface
    that belongs to the Concurrent CDK.
    """

    def __init__(self, cursor: Cursor, stream_slices: Iterable[Optional[Mapping[str, Any]]], read_state_from_cursor: bool = False):
        self._cursor = cursor
        self._stream_slices = iter(stream_slices)
        # read_state_from_cursor is used to delineate that partitions should determine when to stop syncing dynamically according
        # to the value of the state at runtime. This currently only applies to streams that use resumable full refresh.
        self._read_state_from_cursor = read_state_from_cursor
        self._current_slice: Optional[StreamSlice] = None
        self._finished_sync = False

    def next(self) -> Optional[Mapping[str, Any]]:
        """
        The next() method returns the next slice of data should be synced for the current stream according to its cursor.
        This function support iterating over a stream's slices across two dimensions. The first dimension is the stream's
        partitions like parent records for a substream. The inner dimension is iterating over the cursor value like a
        date range for incremental streams or a pagination checkpoint for resumable full refresh.

        basic algorithm for iterating through a stream's slices is:
        1. The first time next() is invoked we get the first partition and return it
        2. For streams whose cursor value is determined dynamically using stream state
            1. Get the current state for the current partition
            2. If the current partition's state is complete, get the next partition
            3. If the current partition's state is still in progress, emit the next cursor value
        3. If a stream has processed all partitions, the iterator will raise a StopIteration exception signaling there are no more
           slices left for extracting more records.
        """

        try:
            if self._current_slice is None:
                self._current_slice = self._get_next_slice()
                return self._current_slice
            if self._read_state_from_cursor:
                state_for_slice = self._cursor.select_state(self._current_slice)
                if state_for_slice == {"__ab_full_refresh_sync_complete": True}:
                    self._current_slice = self._get_next_slice()
                else:
                    self._current_slice = StreamSlice(cursor_slice=state_for_slice or {}, partition=self._current_slice.partition)
            else:
                # Unlike RFR cursors that iterate dynamically based on how stream state is updated, most cursors operate on a
                # fixed set of slices determined before reading records. They should just iterate to the next slice
                self._current_slice = self._get_next_slice()
            return self._current_slice
        except StopIteration:
            self._finished_sync = True
            return None

    def _get_next_slice(self) -> StreamSlice:
        next_slice = next(self._stream_slices)
        if not isinstance(next_slice, StreamSlice):
            raise ValueError(
                f"{self._current_slice} should be of type StreamSlice. This is likely a bug in the CDK, please contact Airbyte support"
            )
        return next_slice

    def observe(self, new_state: Mapping[str, Any]) -> None:
        # Cursor based checkpoint readers don't need to observe the new state because it has already been updated by the cursor
        # while processing records
        pass

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        # This is used to avoid sending a duplicate state message at the end of a sync since the stream has already
        # emitted state at the end of each slice. We only emit state if _current_slice is None which indicates we had no
        # slices and emitted no record or are currently in the process of emitting records.
        if self._current_slice is None or not self._finished_sync:
            return self._cursor.get_stream_state()
        else:
            return None


class ResumableFullRefreshCheckpointReader(CheckpointReader):
    """
    ResumableFullRefreshCheckpointReader allows for iteration over an unbounded set of records based on the pagination strategy
    of the stream. Because the number of pages is unknown, the stream's current state is used to determine whether to continue
    fetching more pages or stopping the sync.
    """

    def __init__(self, stream_state: Mapping[str, Any]):
        # The first attempt of an RFR stream has an empty {} incoming state, but should still make a first attempt to read records
        # from the first page in next().
        self._first_page = bool(stream_state == {})
        self._state: Mapping[str, Any] = stream_state

    def next(self) -> Optional[Mapping[str, Any]]:
        if self._first_page:
            self._first_page = False
            return self._state
        elif self._state == {}:
            return None
        else:
            return self._state

    def observe(self, new_state: Mapping[str, Any]) -> None:
        self._state = new_state

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return self._state or {}


class FullRefreshCheckpointReader(CheckpointReader):
    """
    FullRefreshCheckpointReader iterates over data that cannot be checkpointed incrementally during the sync because the stream
    is not capable of managing state. At the end of a sync, a final state message is emitted to signal completion.
    """

    def __init__(self, stream_slices: Iterable[Optional[Mapping[str, Any]]]):
        self._stream_slices = iter(stream_slices)
        self._final_checkpoint = False

    def next(self) -> Optional[Mapping[str, Any]]:
        try:
            return next(self._stream_slices)
        except StopIteration:
            self._final_checkpoint = True
            return None

    def observe(self, new_state: Mapping[str, Any]) -> None:
        pass

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        if self._final_checkpoint:
            return {"__ab_no_cursor_state_message": True}
        return None
