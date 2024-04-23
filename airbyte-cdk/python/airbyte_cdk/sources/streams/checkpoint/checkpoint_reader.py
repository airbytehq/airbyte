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
        Returns the next slice that will be used to fetch the next group of records
        """

    @abstractmethod
    def observe(self, new_state: Mapping[str, Any]) -> None:
        """
        Updates the internal state of the checkpoint reader based on the incoming stream state from a connector.

        WARNING: This is used to retain backwards compatibility with streams using the legacy get_stream_state() method.
        In order to uptake Resumable Full Refresh, connectors must migrate streams to use the state setter/getter methods.
        """
        # todo blai: Ideally observe and get_checkpoint should just be one method, but because of the legacy state behavior
        #  observation and reading Stream.state checkpoint are not 1:1 with each other

    @abstractmethod
    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        """
        Retrieves the current state value of the stream
        """

    # The separate get_checkpoint() and final_checkpoint() methods make the the two interfaces a little odd because looking at the
    # implementation in isolation, based fields on the implementations of the CheckpointReaders aren't optional.
    @abstractmethod
    def final_checkpoint(self) -> Optional[Mapping[str, Any]]:
        """
        Certain types of streams like full_refresh don't checkpoint per-slice, but should always emit a final state at the end of
        a sync.
        """


class IncrementalCheckpointReader(CheckpointReader):
    """
    IncrementalCheckpointReader handles iterating through a stream based on partitioned windows of data that are determined
    before syncing data.
    """

    def __init__(self, stream_state: Mapping[str, Any], stream_slices: Iterable[Optional[Mapping[str, Any]]]):
        self._state: Mapping[str, Any] = stream_state
        self._stream_slices = iter(stream_slices)

    def next(self) -> Optional[Mapping[str, Any]]:
        try:
            return next(self._stream_slices)
        except StopIteration:
            return None

    def observe(self, new_state: Mapping[str, Any]) -> None:
        self._state = new_state

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return self._state

    def final_checkpoint(self) -> Optional[Mapping[str, Any]]:
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
        #  todo blai: I think this is my main concern with the interface is that it puts a lot of onus on the connector developer to
        #   structure their state object correctly to coincide with how the checkpoint_reader interprets values.
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

    def final_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return self._state  # removed this part which I think we can do because we only emit final state if needed: or {}


class FullRefreshCheckpointReader(CheckpointReader):
    """
    FullRefreshCheckpointReader iterates over data that cannot be checkpointed incrementally during the sync because the stream
    is not capable of managing state. At the end of a sync, a final state message is emitted to signal completion.
    """

    def __init__(self, stream_slices: Iterable[Optional[Mapping[str, Any]]]):
        self._stream_slices = iter(stream_slices)

    def next(self) -> Optional[Mapping[str, Any]]:
        try:
            return next(self._stream_slices)
        except StopIteration:
            return None

    def observe(self, new_state: Mapping[str, Any]) -> None:
        pass

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return None

    def final_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return {"__ab_full_refresh_state_message": True}  # replace this with the new terminal value from ella
