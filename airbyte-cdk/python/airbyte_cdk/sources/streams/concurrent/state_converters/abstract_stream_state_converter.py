#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, List, MutableMapping, Optional, Tuple

if TYPE_CHECKING:
    from airbyte_cdk.sources.streams.concurrent.cursor import CursorField


class ConcurrencyCompatibleStateType(Enum):
    date_range = "date-range"


class AbstractStreamStateConverter(ABC):
    START_KEY = "start"
    END_KEY = "end"

    @abstractmethod
    def _from_state_message(self, value: Any) -> Any:
        pass

    @abstractmethod
    def _to_state_message(self, value: Any) -> Any:
        pass

    def __init__(self, is_sequential_state: bool = True):
        self._is_sequential_state = is_sequential_state

    def convert_to_state_message(self, cursor_field: "CursorField", stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        { "created": "2021-01-18T21:18:20.000Z" }
        """
        if self.is_state_message_compatible(stream_state) and self._is_sequential_state:
            legacy_state = stream_state.get("legacy", {})
            latest_complete_time = self._get_latest_complete_time(stream_state.get("slices", []))
            if latest_complete_time is not None:
                legacy_state.update({cursor_field.cursor_field_key: self._to_state_message(latest_complete_time)})
            return legacy_state or {}
        else:
            return self.serialize(stream_state, ConcurrencyCompatibleStateType.date_range)

    def _get_latest_complete_time(self, slices: List[MutableMapping[str, Any]]) -> Any:
        """
        Get the latest time before which all records have been processed.
        """
        if not slices:
            raise RuntimeError("Expected at least one slice but there were none. This is unexpected; please contact Support.")
        merged_intervals = self.merge_intervals(slices)
        first_interval = merged_intervals[0]

        return first_interval.get("most_recent_cursor_value") or first_interval[self.START_KEY]

    def deserialize(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Perform any transformations needed for compatibility with the converter.
        """
        for stream_slice in state.get("slices", []):
            stream_slice[self.START_KEY] = self._from_state_message(stream_slice[self.START_KEY])
            stream_slice[self.END_KEY] = self._from_state_message(stream_slice[self.END_KEY])
        return state

    def serialize(self, state: MutableMapping[str, Any], state_type: ConcurrencyCompatibleStateType) -> MutableMapping[str, Any]:
        """
        Perform any transformations needed for compatibility with the converter.
        """
        serialized_slices = []
        for stream_slice in state.get("slices", []):
            serialized_slices.append(
                {
                    self.START_KEY: self._to_state_message(stream_slice[self.START_KEY]),
                    self.END_KEY: self._to_state_message(stream_slice[self.END_KEY]),
                }
            )
        return {"slices": serialized_slices, "state_type": state_type.value}

    @staticmethod
    def is_state_message_compatible(state: MutableMapping[str, Any]) -> bool:
        return bool(state) and state.get("state_type") in [t.value for t in ConcurrencyCompatibleStateType]

    @abstractmethod
    def convert_from_sequential_state(
        self,
        cursor_field: "CursorField",  # to deprecate as it is only needed for sequential state
        stream_state: MutableMapping[str, Any],
        start: Optional[Any],
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        """
        Convert the state message to the format required by the ConcurrentCursor.

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
    def increment(self, value: Any) -> Any:
        """
        Increment a timestamp by a single unit.
        """
        ...

    def merge_intervals(self, intervals: List[MutableMapping[str, Any]]) -> List[MutableMapping[str, Any]]:
        """
        Compute and return a list of merged intervals.

        Intervals may be merged if the start time of the second interval is 1 unit or less (as defined by the
        `increment` method) than the end time of the first interval.
        """
        if not intervals:
            return []

        sorted_intervals = sorted(intervals, key=lambda interval: (interval[self.START_KEY], interval[self.END_KEY]))
        merged_intervals = [sorted_intervals[0]]

        for current_interval in sorted_intervals[1:]:
            last_interval = merged_intervals[-1]
            last_interval_end = last_interval[self.END_KEY]
            current_interval_start = current_interval[self.START_KEY]

            if self.increment(last_interval_end) >= current_interval_start:
                last_interval[self.END_KEY] = max(last_interval_end, current_interval[self.END_KEY])
                last_interval_cursor_value = last_interval.get("most_recent_cursor_value")
                current_interval_cursor_value = current_interval.get("most_recent_cursor_value")

                last_interval["most_recent_cursor_value"] = (
                    max(current_interval_cursor_value, last_interval_cursor_value)
                    if current_interval_cursor_value and last_interval_cursor_value
                    else current_interval_cursor_value or last_interval_cursor_value
                )
            else:
                # Add a new interval if no overlap
                merged_intervals.append(current_interval)

        return merged_intervals

    @abstractmethod
    def parse_value(self, value: Any) -> Any:
        """
        Parse the value of the cursor field into a comparable value.
        """
        ...

    @property
    @abstractmethod
    def zero_value(self) -> Any:
        ...
