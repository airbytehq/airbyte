#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable, List, MutableMapping, Optional

import pendulum
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
    ConcurrencyCompatibleStateType,
)
from pendulum.datetime import DateTime


class DateTimeStreamStateConverter(AbstractStreamStateConverter):
    START_KEY = "start_date"
    END_KEY = "end_date"

    @property
    @abstractmethod
    def _zero_value(self) -> Any:
        ...

    @property
    def zero_value(self) -> datetime:
        return self.parse_timestamp(self._zero_value)

    @abstractmethod
    def decrement(self, timestamp: datetime) -> datetime:
        ...

    @abstractmethod
    def parse_timestamp(self, timestamp: Any) -> datetime:
        ...

    @abstractmethod
    def output_format(self, timestamp: datetime) -> Any:
        ...

    def deserialize(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if "low_water_mark" in state:
            state["low_water_mark"] = self.parse_timestamp(state["low_water_mark"])
        return state

    def parse_value(self, value: Any) -> Any:
        """
        Parse the value of the cursor field into a comparable value.
        """
        return self.parse_timestamp(value)

    def is_greater_than(self, end_time: Optional[Any], start_time: Optional[Any]) -> bool:
        if end_time is None:
            return False
        if start_time is None:
            return True
        return end_time > start_time

    def convert_from_sequential_state(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message to the format required by the ConcurrentCursor.

        e.g.
        {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "metadata": { … },
            "low_water_mark": "2021-01-18T21:18:20.000.000Z"
        }
        """
        if cursor_field.cursor_field_key and cursor_field.cursor_field_key in stream_state:
            low_water_mark = self.parse_timestamp(stream_state[cursor_field.cursor_field_key])
        else:
            low_water_mark = None
        return {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "low_water_mark":  low_water_mark,
            "legacy": stream_state,
        }

    def convert_to_sequential_state(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        { "created": "2021-01-18T21:18:20.000Z" }
        """
        if self.is_state_message_compatible(stream_state):
            legacy_state = stream_state.get("legacy", {})
            if "low_water_mark" in stream_state:
                if low_water_mark := stream_state["low_water_mark"]:
                    legacy_state.update({cursor_field.cursor_field_key: self.output_format(low_water_mark)})
            return legacy_state or {}
        else:
            return stream_state

    def min(self, *items: Iterable[Any]) -> Any:
        """
        Performs a comparison of the items and returns the min.
        """
        return min(*items)

    def max(self, *items: Iterable[Any]) -> Any:
        """
        Performs a comparison of the items and returns the max.
        """
        return max(*items)


class EpochValueConcurrentStreamStateConverter(DateTimeStreamStateConverter):
    """
    e.g.
    { "created": 1617030403 }
    =>
    {
        "state_type": "date-range",
        "metadata": { … },
        "low_water_mark": 1617030403
    }
    """

    _zero_value = 0

    def decrement(self, timestamp: datetime) -> datetime:
        return timestamp - timedelta(seconds=1)

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
        "low_water_mark": "2020-01-18T21:18:20.000Z"
    }
    """

    _zero_value = "0001-01-01T00:00:00.000Z"

    def decrement(self, timestamp: datetime) -> datetime:
        return timestamp - timedelta(milliseconds=1)

    def output_format(self, timestamp: datetime) -> Any:
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def parse_timestamp(self, timestamp: str) -> datetime:
        dt_object = pendulum.parse(timestamp)
        if not isinstance(dt_object, DateTime):
            raise ValueError(f"DateTime object was expected but got {type(dt_object)} from pendulum.parse({timestamp})")
        return dt_object  # type: ignore  # we are manually type checking because pendulum.parse may return different types
