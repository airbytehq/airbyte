# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterable, Mapping, MutableMapping, Optional


class CheckpointMode(Enum):
    INCREMENTAL = "incremental"
    RESUMABLE_FULL_REFRESH = "resumable_full_refresh"
    FULL_REFRESH = "full_refresh"


class CheckpointReader(ABC):
    @abstractmethod
    def next(self) -> Optional[MutableMapping[str, Any]]:
        """
        Returns the next slice to process
        """

    @abstractmethod
    def observe(self, new_state: Mapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Updates the internal state of the checkpoint reader based on the incoming stream state from a connector.

        WARNING: This is used to retain backwards compatibility with streams using the legacy get_stream_state() method.
        In order to uptake Resumable Full Refresh, connectors must migrate streams to use the state setter/getter methods.
        """

    @abstractmethod
    def read_state(self) -> MutableMapping[str, Any]:
        """
        This is interesting. With this move, we've turned checkpoint reader to resemble even more of a cursor because we are acting
        even more like an intermediary since we are more regularly assigning Stream.state to CheckpointReader._state via observe
        """


class IncrementalCheckpointReader(CheckpointReader):
    def __init__(self, stream_slices: Iterable[Optional[Mapping[str, Any]]]):
        self._state = None
        self._stream_slices = iter(stream_slices)

    def next(self) -> Optional[MutableMapping[str, Any]]:
        try:
            return next(self._stream_slices)
        except StopIteration:
            return None

    def observe(self, new_state: Mapping[str, Any]):
        # This is really only needed for backward compatibility with the legacy state management implementations.
        # We only update the underlying _state value for legacy, otherwise managing state is done by the connector implementation
        self._state = new_state

    def read_state(self) -> MutableMapping[str, Any]:
        return self._state


class ResumableFullRefreshCheckpointReader(CheckpointReader):
    def __init__(self, stream_state: MutableMapping[str, Any]):
        self._state: Optional[MutableMapping[str, Any]] = stream_state
        # can i have a dummy for first iteration to trigger the loop, and subsequent ones, we see {} and then therefor end the loop

    def next(self) -> Optional[MutableMapping[str, Any]]:
        return self._state

    def observe(self, new_state: Mapping[str, Any]):
        # observe() was originally just for backwards compatibility, but we can potentially fold it more into the the read_records()
        # flow as I've coded out so far.
        self._state = new_state

    def read_state(self) -> MutableMapping[str, Any]:
        return self._state or {}


class FullRefreshCheckpointReader(CheckpointReader):
    def __init__(self):
        self._stream_slices = iter([{}])

    def next(self) -> Optional[MutableMapping[str, Any]]:
        try:
            return next(self._stream_slices)
        except StopIteration:
            return None

    def observe(self, new_state: Mapping[str, Any]):
        pass

    def read_state(self) -> MutableMapping[str, Any]:
        return {"__ab_is_sync_complete": True}  # replace this with the new terminal value from ella
