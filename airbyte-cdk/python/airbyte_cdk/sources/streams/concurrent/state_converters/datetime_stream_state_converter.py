#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, MutableMapping, Optional, Tuple

import pendulum
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
    ConcurrencyCompatibleStateType,
)
from pendulum.datetime import DateTime


class DateTimeStreamStateConverter(AbstractStreamStateConverter):
    def _from_state_message(self, value: Any) -> Any:
        return self.parse_timestamp(value)

    def _to_state_message(self, value: Any) -> Any:
        return self.output_format(value)

    @property
    @abstractmethod
    def _zero_value(self) -> Any:
        ...

    @property
    def zero_value(self) -> datetime:
        return self.parse_timestamp(self._zero_value)

    @classmethod
    def get_end_provider(cls) -> Callable[[], datetime]:
        return lambda: datetime.now(timezone.utc)

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

    def _compare_intervals(self, end_time: Any, start_time: Any) -> bool:
        return bool(self.increment(end_time) >= start_time)

    def convert_from_sequential_state(
        self, cursor_field: CursorField, stream_state: MutableMapping[str, Any], start: Optional[datetime]
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
        slices = [{self.START_KEY: start if start is not None else sync_start, self.END_KEY: sync_start}]

        return sync_start, {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "slices": slices,
            "legacy": stream_state,
        }

    def _get_sync_start(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any], start: Optional[datetime]) -> datetime:
        sync_start = start if start is not None else self.zero_value
        prev_sync_low_water_mark = (
            self.parse_timestamp(stream_state[cursor_field.cursor_field_key]) if cursor_field.cursor_field_key in stream_state else None
        )
        if prev_sync_low_water_mark and prev_sync_low_water_mark >= sync_start:
            return prev_sync_low_water_mark
        else:
            return sync_start


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
