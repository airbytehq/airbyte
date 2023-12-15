#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, MutableMapping, Optional

import pendulum


class ConcurrencyCompatibleStateType(Enum):
    date_range = "date-range"


class ConcurrentStreamStateConverter(ABC):
    START_KEY = "start"
    END_KEY = "end"

    def __init__(self, cursor_field: str):
        self._cursor_field = cursor_field

    @property
    @abstractmethod
    def zero_value(self) -> Any:
        ...

    def get_concurrent_stream_state(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if self.is_state_message_compatible(state):
            return state
        return self.convert_from_sequential_state(state)

    @staticmethod
    def is_state_message_compatible(state: MutableMapping[str, Any]) -> bool:
        return bool(state) and state.get("state_type") in [t.value for t in ConcurrencyCompatibleStateType]

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
    def increment(self, timestamp: Any) -> Any:
        """
        Increment a timestamp by a single unit.
        """
        ...

    @abstractmethod
    def merge_intervals(self, intervals: List[MutableMapping[str, Any]]) -> List[MutableMapping[str, Any]]:
        """
        Compute and return a list of merged intervals.

        Intervals may be merged if the start time of the second interval is 1 unit or less (as defined by the
        `increment` method) than the end time of the first interval.
        """
        ...


class EpochValueConcurrentStreamStateConverter(ConcurrentStreamStateConverter):
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

    START_KEY = "start"
    END_KEY = "end"
    zero_value = 0

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
        if self.is_state_message_compatible(stream_state):
            return stream_state
        if self._cursor_field in stream_state:
            slices = [
                {
                    self.START_KEY: self.zero_value,
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

    def convert_to_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        { "created": 1617030403 }
        """
        if self.is_state_message_compatible(stream_state):
            legacy_state = stream_state.get("legacy", {})
            if slices := stream_state.pop("slices", None):
                legacy_state.update({self._cursor_field: self._get_latest_complete_time(slices)})
            return legacy_state or {}
        else:
            return stream_state

    def _get_latest_complete_time(self, slices: List[MutableMapping[str, Any]]) -> Optional[Any]:
        """
        Get the latest time before which all records have been processed.
        """
        if slices:
            first_interval = self.merge_intervals(slices)[0][self.END_KEY]
            return first_interval
        else:
            return None

    def increment(self, timestamp: Any) -> Any:
        return timestamp + 1

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


class IsoMillisConcurrentStreamStateConverter(ConcurrentStreamStateConverter):
    def __init__(self, cursor_field: str, slice_timestamp_format: str):
        super().__init__(cursor_field)
        self._slice_timestamp_format = slice_timestamp_format

    @property
    def zero_value(self) -> str:
        return datetime(1, 1, 1, 0, 0, 0, 0).strftime(self._slice_timestamp_format)

    def increment(self, timestamp: Any) -> Any:
        timestamp_obj = pendulum.parse(timestamp)
        return datetime.strftime(timestamp_obj + timedelta(milliseconds=1), self._slice_timestamp_format)

    def convert_from_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message to the format required by the ThreadBasedConcurrentStream.

        e.g.
        {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "metadata": { … },
            "slices": [
                {starts: 0, end: "2021-01-18T21:18:20.000+00:00", finished_processing: true}]
        }
        """
        if self.is_state_message_compatible(stream_state):
            return stream_state
        if self._cursor_field in stream_state:
            slices = [
                {
                    # TODO: if we migrate stored state to the concurrent state format, we may want this to be the config start date
                    # instead of `zero_value`
                    self.START_KEY: self.zero_value,
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

    def convert_to_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        { "created": "2021-01-18T21:18:20.000Z" }
        """
        if self.is_state_message_compatible(stream_state):
            legacy_state = stream_state.get("legacy", {})
            if slices := stream_state.pop("slices", None):
                legacy_state.update({self._cursor_field: self._millis_format(self._get_latest_complete_time(slices))})
            return legacy_state or {}
        else:
            return stream_state

    def _millis_format(self, timestamp: Optional[str]) -> Optional[str]:
        return pendulum.parse(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if timestamp else None

    def _get_latest_complete_time(self, slices: List[MutableMapping[str, Any]]) -> Optional[str]:
        """
        Get the latest time before which all records have been processed.
        """
        if slices:
            first_interval = self.merge_intervals(slices)[0][self.END_KEY]
            return first_interval
        else:
            return None

    def merge_intervals(self, intervals: List[MutableMapping[str, Any]]) -> List[MutableMapping[str, str]]:
        sorted_intervals = sorted(intervals, key=lambda x: (pendulum.parse(x[self.START_KEY]), pendulum.parse(x[self.END_KEY])))
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
