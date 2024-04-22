# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterable, Mapping, Optional


class CheckpointMode(Enum):
    INCREMENTAL = "incremental"
    RESUMABLE_FULL_REFRESH = "resumable_full_refresh"
    FULL_REFRESH = "full_refresh"


class CheckpointReader(ABC):
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
        This is interesting. With this move, we've turned checkpoint reader to resemble even more of a cursor because we are acting
        even more like an intermediary since we are more regularly assigning Stream.state to CheckpointReader._state via observe
        """

    # It would be interesting if we wanted to get rid of this. Right now the main use case for a different get_checkpoint
    # and final_checkpoint is for a full refresh substream we don't want to checkpoint after every slice because there is not
    # a meaningful state value to emit.
    @abstractmethod
    def final_checkpoint(self) -> Optional[Mapping[str, Any]]:
        """
        Certain types of streams like full_refresh don't checkpoint per-slice, but should always emit a final state at the end of
        a sync.
        """


class IncrementalCheckpointReader(CheckpointReader):
    def __init__(self, stream_slices: Iterable[Optional[Mapping[str, Any]]]):
        self._state: Optional[Mapping[str, Any]] = None
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
    def __init__(self, stream_state: Mapping[str, Any]):
        self._state: Optional[Mapping[str, Any]] = stream_state or {"first_slice": True}
        # can i have a dummy for first iteration to trigger the loop, and subsequent ones, we see {} and then therefor end the loop

    def next(self) -> Optional[Mapping[str, Any]]:
        # todo blai: Does it feel weird that we only observe real maps, but treat empty map as stop iterating?
        #  I don't love forcing the developer to do more, but a terminal state finished value might be nice instead of assuming {}
        #  I think this is my main concern with the interface is that it puts a lot of onus on the connector developer to structure
        #  their state object correctly to coincide with how the checkpoint_reader interprets values.
        return None if self._state == {} else self._state
        # return None if self._state.get("is_done") else self._state

    def observe(self, new_state: Mapping[str, Any]) -> None:
        self._state = new_state

    def get_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return self._state or {}

    def final_checkpoint(self) -> Optional[Mapping[str, Any]]:
        return self._state  # removed this part which I think we can do because we only emit final state if needed: or {}


class FullRefreshCheckpointReader(CheckpointReader):
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
