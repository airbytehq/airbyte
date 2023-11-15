#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, List, MutableMapping, Optional, Callable


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

    @abstractmethod
    def min(self) -> Any:
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

    def merge_intervals(self, intervals: List[MutableMapping[str, Any]]) -> List[MutableMapping[str, Any]]:
        sorted_intervals = sorted(intervals, key=lambda x: (x[self.START_KEY], x[self.END_KEY]))
        if len(sorted_intervals) > 0:
            merged_intervals = [sorted_intervals[0]]
        else:
            return []
        for interval in sorted_intervals[1:]:
            if interval[self.START_KEY] <= self.increment(merged_intervals[-1][self.END_KEY]):
                merged_intervals[-1][self.END_KEY] = interval[self.END_KEY]
            else:
                merged_intervals.append(interval)

        return merged_intervals


class AscendingValueConcurrentStreamStateConverter(ConcurrentStreamStateConverter):
    def __init__(self, cursor_field: str, min_value: Any, increment_function: Callable[[Any], Any]):
        self._cursor_field = cursor_field
        self._min_value = min_value
        self._increment_function = increment_function

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
        if self._cursor_field in stream_state and stream_state[self._cursor_field]:
            slices = [
                {
                    self.START_KEY: self.min(),
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

    def increment(self, timestamp: Any) -> Any:
        return self._increment_function(timestamp)

    def min(self) -> Any:
        return self._min_value
