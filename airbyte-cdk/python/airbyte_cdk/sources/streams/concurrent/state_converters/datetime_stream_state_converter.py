#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, List, MutableMapping, Optional

import pendulum

from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
    ConcurrencyCompatibleStateType,
)

class DateTimeStreamStateConverter(AbstractStreamStateConverter):
    START_KEY = "start"
    END_KEY = "end"

    @property
    def zero_value(self) -> datetime:
        return datetime(1, 1, 1, 0, 0, 0, 0)

    @abstractmethod
    def increment(self, timestamp: datetime) -> datetime:
        ...

    @abstractmethod
    def parse_timestamp(self, timestamp: Any) -> datetime:
        ...

    @abstractmethod
    def output_format(self, timestamp: datetime) -> Any:
        ...

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
            if self.compare_intervals(last_end_time, current_start_time):
                merged_end_time = max(last_end_time, interval[self.END_KEY])
                merged_intervals[-1][self.END_KEY] = merged_end_time
            else:
                merged_intervals.append(interval)

        return merged_intervals

    def compare_intervals(self, end_time, start_time):
        return self.increment(end_time) >= start_time

    def convert_from_sequential_state(self, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message to the format required by the ConcurrentCursor.

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
                    self.END_KEY: self.parse_timestamp(stream_state[self._cursor_field]),
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
                legacy_state.update({self._cursor_field: self.output_format(self._get_latest_complete_time(slices))})
            return legacy_state or {}
        else:
            return stream_state

    def _get_latest_complete_time(self, slices: List[MutableMapping[str, Any]]) -> Optional[datetime]:
        """
        Get the latest time before which all records have been processed.
        """
        if slices:
            first_interval = self.merge_intervals(slices)[0][self.END_KEY]
            return first_interval
        else:
            return None


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

    def increment(self, timestamp: datetime) -> Any:
        return timestamp + timedelta(seconds=1)

    def output_format(self, timestamp: datetime) -> int:
        return int(timestamp.timestamp())

    def parse_timestamp(self, timestamp: int) -> datetime:
        return pendulum.from_timestamp(timestamp)


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

    def __init__(self, cursor_field: str, slice_timestamp_format: str):
        super().__init__(cursor_field)
        self._slice_timestamp_format = slice_timestamp_format

    def increment(self, timestamp: datetime) -> Any:
        return timestamp + timedelta(milliseconds=1)

    def output_format(self, timestamp: datetime) -> Any:
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def parse_timestamp(self, timestamp: str) -> datetime:
        return pendulum.parse(timestamp)
