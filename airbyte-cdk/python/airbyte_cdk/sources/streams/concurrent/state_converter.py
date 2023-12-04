#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, MutableMapping, Optional


class ConcurrencyCompatibleStateType(Enum):
    date_range = "date-range"


class ConcurrentStreamStateConverter(ABC):
    START_KEY = "start"
    END_KEY = "end"

    def get_concurrent_stream_state(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if self.is_state_message_compatible(state):
            return state
        return self.convert_from_sequential_state(state)

    @staticmethod
    def is_state_message_compatible(state: MutableMapping[str, Any]) -> bool:
        return state.get("state_type") in [t.value for t in ConcurrencyCompatibleStateType]

    @abstractmethod
    def convert_from_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message to the format required by the ThreadBasedConcurrentStream.

        e.g.
        {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "metadata": { … },
            "slices": [
                {starts: 0, end: 1617030403, finished_processing: true}]
        }
        """
        ...

    @abstractmethod
    def convert_to_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        { "created": 1617030403 }
        """
        ...

    def _get_latest_complete_time(self, slices: List[MutableMapping[str, Any]]) -> Optional[Any]:
        """
        Get the latest time before which all records have been processed.
        """
        if slices:
            first_interval = self.merge_intervals(slices)[0][self.END_KEY]
            return first_interval
        else:
            return None

    @staticmethod
    @abstractmethod
    def increment(timestamp: Any) -> Any:
        """
        Increment a timestamp by a single unit.
        """
        ...

    @classmethod
    def merge_intervals(cls, intervals: List[MutableMapping[str, Any]]) -> List[MutableMapping[str, Any]]:
        sorted_intervals = sorted(intervals, key=lambda x: (x[cls.START_KEY], x[cls.END_KEY]))
        if len(sorted_intervals) > 0:
            merged_intervals = [sorted_intervals[0]]
        else:
            return []
        for interval in sorted_intervals[1:]:
            if interval[cls.START_KEY] <= cls.increment(merged_intervals[-1][cls.END_KEY]):
                merged_intervals[-1][cls.END_KEY] = interval[cls.END_KEY]
            else:
                merged_intervals.append(interval)

        return merged_intervals


class EpochValueConcurrentStreamStateConverter(ConcurrentStreamStateConverter):
    def __init__(self, cursor_field: str):
        self._cursor_field = cursor_field

    def convert_from_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        e.g.
        { "created": 1617030403 }
        =>
        {
            "state_type": "date-range",
            "metadata": { … },
            "slices": [
                {starts: 0, end: 1617030403, finished_processing: true}
            ]
        }
        """
        if self.is_state_message_compatible(stream_state):
            return stream_state
        if self._cursor_field in stream_state:
            slices = [
                {
                    self.START_KEY: 0,
                    self.END_KEY: stream_state[self._cursor_field],
                },
            ]
        else:
            slices = []
        return {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "slices": slices,
            "legacy": stream_state,
        }

    def convert_to_sequential_state(self, stream_state: MutableMapping[str, Any]) -> Any:
        """
        e.g.
        {
            "state_type": "date-range",
            "metadata": { … },
            "slices": [
                {starts: 0, end: 1617030403, finished_processing: true}
            ]
        }
        =>
        { "created": 1617030403 }
        """
        if self.is_state_message_compatible(stream_state):
            legacy_state = stream_state.get("legacy", {})
            if slices := stream_state.pop("slices", None):
                legacy_state.update({self._cursor_field: self._get_latest_complete_time(slices)})
            return legacy_state
        else:
            return stream_state

    @staticmethod
    def increment(timestamp: Any) -> Any:
        return timestamp + 1
