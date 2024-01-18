#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, List, MutableMapping, Optional, Tuple

import pendulum
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
    ConcurrencyCompatibleStateType,
)
from pendulum.datetime import DateTime


class DateTimeStreamStateConverter(AbstractStreamStateConverter):
    @property
    @abstractmethod
    def _zero_value(self) -> Any:
        ...

    @property
    def zero_value(self) -> datetime:
        return self.parse_timestamp(self._zero_value)

    @abstractmethod
    def increment(self, timestamp: datetime) -> datetime:
        ...

    @abstractmethod
    def parse_timestamp(self, timestamp: Any) -> datetime:
        ...

    @abstractmethod
    def output_format(self, timestamp: datetime) -> Any:
        ...

    def deserialize(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        for stream_slice in state.get("slices", []):
            stream_slice[self.START_KEY] = self.parse_timestamp(stream_slice[self.START_KEY])
            stream_slice[self.END_KEY] = self.parse_timestamp(stream_slice[self.END_KEY])
        return state

    def parse_value(self, value: Any) -> Any:
        """
        Parse the value of the cursor field into a comparable value.
        """
        return self.parse_timestamp(value)

    def merge_intervals(self, intervals: List[MutableMapping[str, datetime]]) -> List[MutableMapping[str, datetime]]:
        if not intervals:
            return []

        sorted_intervals = sorted(intervals, key=lambda x: (x[self.START_KEY], x[self.END_KEY]))
        merged_intervals = [sorted_intervals[0]]

        for interval in sorted_intervals[1:]:
            last_end_time = merged_intervals[-1][self.END_KEY]
            current_start_time = interval[self.START_KEY]
            if self._compare_intervals(last_end_time, current_start_time):
                merged_end_time = max(last_end_time, interval[self.END_KEY])
                merged_intervals[-1][self.END_KEY] = merged_end_time
            else:
                merged_intervals.append(interval)

        return merged_intervals

    def _compare_intervals(self, end_time: Any, start_time: Any) -> bool:
        return bool(self.increment(end_time) >= start_time)

    def convert_from_sequential_state(
        self, cursor_field: CursorField, stream_state: MutableMapping[str, Any], start: datetime
    ) -> Tuple[datetime, MutableMapping[str, Any]]:
        """
        Convert the state message to the format required by the ConcurrentCursor.

        e.g.
        {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "metadata": { … },
            "slices": [
                {"start": "2021-01-18T21:18:20.000+00:00", "end": "2021-01-18T21:18:20.000+00:00"},
            ]
        }
        """
        sync_start = self._get_sync_start(cursor_field, stream_state, start)
        if self.is_state_message_compatible(stream_state):
            return sync_start, stream_state

        # Create a slice to represent the records synced during prior syncs.
        # The start and end are the same to avoid confusion as to whether the records for this slice
        # were actually synced
        slices = [{self.START_KEY: sync_start, self.END_KEY: sync_start}]

        return sync_start, {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "slices": slices,
            "legacy": stream_state,
        }

    def _get_sync_start(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any], start: Optional[Any]) -> datetime:
        sync_start = self.parse_timestamp(start) if start is not None else self.zero_value
        prev_sync_low_water_mark = (
            self.parse_timestamp(stream_state[cursor_field.cursor_field_key]) if cursor_field.cursor_field_key in stream_state else None
        )
        if prev_sync_low_water_mark and prev_sync_low_water_mark >= sync_start:
            return prev_sync_low_water_mark
        else:
            return sync_start

    def convert_to_sequential_state(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        { "created": "2021-01-18T21:18:20.000Z" }
        """
        if self.is_state_message_compatible(stream_state):
            legacy_state = stream_state.get("legacy", {})
            latest_complete_time = self._get_latest_complete_time(stream_state.get("slices", []))
            if latest_complete_time is not None:
                legacy_state.update({cursor_field.cursor_field_key: self.output_format(latest_complete_time)})
            return legacy_state or {}
        else:
            return stream_state

    def _get_latest_complete_time(self, slices: List[MutableMapping[str, Any]]) -> Optional[datetime]:
        """
        Get the latest time before which all records have been processed.
        """
        if not slices:
            raise RuntimeError("Expected at least one slice but there were none. This is unexpected; please contact Support.")

        merged_intervals = self.merge_intervals(slices)
        first_interval = merged_intervals[0]
        return first_interval[self.END_KEY]


class EpochValueConcurrentStreamStateConverter(DateTimeStreamStateConverter):
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

    _zero_value = 0

    def increment(self, timestamp: datetime) -> datetime:
        return timestamp + timedelta(seconds=1)

    def output_format(self, timestamp: datetime) -> int:
        return int(timestamp.timestamp())

    def parse_timestamp(self, timestamp: int) -> datetime:
        dt_object = pendulum.from_timestamp(timestamp)
        if not isinstance(dt_object, DateTime):
            raise ValueError(f"DateTime object was expected but got {type(dt_object)} from pendulum.parse({timestamp})")
        return dt_object  # type: ignore  # we are manually type checking because pendulum.parse may return different types


class IsoMillisConcurrentStreamStateConverter(DateTimeStreamStateConverter):
    """
    e.g.
    { "created": "2021-01-18T21:18:20.000Z" }
    =>
    {
        "state_type": "date-range",
        "metadata": { … },
        "slices": [
            {starts: "2020-01-18T21:18:20.000Z", end: "2021-01-18T21:18:20.000Z", finished_processing: true}
        ]
    }
    """

    _zero_value = "0001-01-01T00:00:00.000Z"

    def increment(self, timestamp: datetime) -> datetime:
        return timestamp + timedelta(milliseconds=1)

    def output_format(self, timestamp: datetime) -> Any:
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def parse_timestamp(self, timestamp: str) -> datetime:
        dt_object = pendulum.parse(timestamp)
        if not isinstance(dt_object, DateTime):
            raise ValueError(f"DateTime object was expected but got {type(dt_object)} from pendulum.parse({timestamp})")
        return dt_object  # type: ignore  # we are manually type checking because pendulum.parse may return different types
