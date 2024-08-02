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


FULL_REFRESH_COMPLETE_STATE: Mapping[str, Any] = {"__ab_full_refresh_sync_complete": True}


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
        try:
            self.current_slice = self._find_next_slice()
            return self.current_slice
        except StopIteration:
            self._finished_sync = True
            return None

    def observe(self, new_state: Mapping[str, Any]) -> None:
        # Cursor based checkpoint readers don't need to observe the new state because it has already been updated by the cursor
        # while processing records
        pass

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        # This is used to avoid sending a duplicate state message at the end of a sync since the stream has already
        # emitted state at the end of each slice. We only emit state if _current_slice is None which indicates we had no
        # slices and emitted no record or are currently in the process of emitting records.
        if self.current_slice is None or not self._finished_sync:
            return self._cursor.get_stream_state()
        else:
            return None

    def _find_next_slice(self) -> StreamSlice:
        """
        _find_next_slice() returns the next slice of data should be synced for the current stream according to its cursor.
        This function supports iterating over a stream's slices across two dimensions. The first dimension is the stream's
        partitions like parent records for a substream. The inner dimension iterates over the cursor value like a date
        range for incremental streams or a pagination checkpoint for resumable full refresh.

        The basic algorithm for iterating through a stream's slices is:
        1. The first time next() is invoked we get the first partition
        2. If the current partition is already complete as a result of a previous sync attempt, continue iterating until
           we find an un-synced partition.
        2. For streams whose cursor value is determined dynamically using stream state
            1. Get the state for the current partition
            2. If the current partition's state is complete, continue iterating over partitions
            3. If the current partition's state is still in progress, emit the next cursor value
            4. If the current partition is complete as delineated by the sentinel value, get the next incomplete partition
        3. When stream has processed all partitions, the iterator will raise a StopIteration exception signaling there are no more
           slices left for extracting more records.
        """

        if self._read_state_from_cursor:
            if self.current_slice is None:
                # current_slice is None represents the first time we are iterating over a stream's slices. The first slice to
                # sync not been assigned yet and must first be read from the iterator
                next_slice = self.read_and_convert_slice()
                state_for_slice = self._cursor.select_state(next_slice)
                if state_for_slice == FULL_REFRESH_COMPLETE_STATE:
                    # Skip every slice that already has the terminal complete value indicating that a previous attempt
                    # successfully synced the slice
                    has_more = True
                    while has_more:
                        next_slice = self.read_and_convert_slice()
                        state_for_slice = self._cursor.select_state(next_slice)
                        has_more = state_for_slice == FULL_REFRESH_COMPLETE_STATE
                return StreamSlice(cursor_slice=state_for_slice or {}, partition=next_slice.partition)
            else:
                state_for_slice = self._cursor.select_state(self.current_slice)
                if state_for_slice == FULL_REFRESH_COMPLETE_STATE:
                    # If the current slice is is complete, move to the next slice and skip the next slices that already
                    # have the terminal complete value indicating that a previous attempt was successfully read.
                    # Dummy initialization for mypy since we'll iterate at least once to get the next slice
                    next_candidate_slice = StreamSlice(cursor_slice={}, partition={})
                    has_more = True
                    while has_more:
                        next_candidate_slice = self.read_and_convert_slice()
                        state_for_slice = self._cursor.select_state(next_candidate_slice)
                        has_more = state_for_slice == FULL_REFRESH_COMPLETE_STATE
                    return StreamSlice(cursor_slice=state_for_slice or {}, partition=next_candidate_slice.partition)
                # The reader continues to process the current partition if it's state is still in progress
                return StreamSlice(cursor_slice=state_for_slice or {}, partition=self.current_slice.partition)
        else:
            # Unlike RFR cursors that iterate dynamically according to how stream state is updated, most cursors operate
            # on a fixed set of slices determined before reading records. They just iterate to the next slice
            return self.read_and_convert_slice()

    @property
    def current_slice(self) -> Optional[StreamSlice]:
        return self._current_slice

    @current_slice.setter
    def current_slice(self, value: StreamSlice) -> None:
        self._current_slice = value

    def read_and_convert_slice(self) -> StreamSlice:
        next_slice = next(self._stream_slices)
        if not isinstance(next_slice, StreamSlice):
            raise ValueError(
                f"{self.current_slice} should be of type StreamSlice. This is likely a bug in the CDK, please contact Airbyte support"
            )
        return next_slice


class LegacyCursorBasedCheckpointReader(CursorBasedCheckpointReader):
    """
    This (unfortunate) class operates like an adapter to retain backwards compatibility with legacy sources that take in stream_slice
    in the form of a Mapping instead of the StreamSlice object. Internally, the reader still operates over StreamSlices, but it
    is instantiated with and emits stream slices in the form of a Mapping[str, Any]. The logic of how partitions and cursors
    are iterated over is synonymous with CursorBasedCheckpointReader.

    We also retain the existing top level fields defined by the connector so the fields are present on dependent methods. For example,
    the resulting mapping structure passed back to the stream's read_records() method looks like:
    {
      "cursor_slice": {
        "next_page_token": 10
      },
      "partition": {
        "repository": "airbytehq/airbyte"
      },
      "next_page_token": 10,
      "repository": "airbytehq/airbyte"
    }
    """

    def __init__(self, cursor: Cursor, stream_slices: Iterable[Optional[Mapping[str, Any]]], read_state_from_cursor: bool = False):
        super().__init__(cursor=cursor, stream_slices=stream_slices, read_state_from_cursor=read_state_from_cursor)

    def next(self) -> Optional[Mapping[str, Any]]:
        try:
            self.current_slice = self._find_next_slice()

            if "partition" in dict(self.current_slice):
                raise ValueError("Stream is configured to use invalid stream slice key 'partition'")
            elif "cursor_slice" in dict(self.current_slice):
                raise ValueError("Stream is configured to use invalid stream slice key 'cursor_slice'")

            # We convert StreamSlice to a regular mapping because legacy connectors operate on the basic Mapping object. We
            # also duplicate all fields at the top level for backwards compatibility for existing Python sources
            return {
                "partition": self.current_slice.partition,
                "cursor_slice": self.current_slice.cursor_slice,
                **dict(self.current_slice),
            }
        except StopIteration:
            self._finished_sync = True
            return None

    def read_and_convert_slice(self) -> StreamSlice:
        next_mapping_slice = next(self._stream_slices)
        if not isinstance(next_mapping_slice, Mapping):
            raise ValueError(
                f"{self.current_slice} should be of type Mapping. This is likely a bug in the CDK, please contact Airbyte support"
            )

        # The legacy reader is instantiated with an iterable of stream slice mappings. We convert each into a StreamSlice
        # to sanely process them during the sync and to reuse the existing Python defined cursors
        return StreamSlice(
            partition=next_mapping_slice,
            cursor_slice={},
        )


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
        elif self._state == FULL_REFRESH_COMPLETE_STATE:
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
