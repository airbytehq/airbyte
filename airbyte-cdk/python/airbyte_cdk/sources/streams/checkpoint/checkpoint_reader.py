# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterable, Mapping, Optional


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
