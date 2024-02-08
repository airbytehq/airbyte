#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, List, MutableMapping, Tuple

if TYPE_CHECKING:
    from airbyte_cdk.sources.streams.concurrent.cursor import CursorField


class ConcurrencyCompatibleStateType(Enum):
    date_range = "date-range"


class AbstractStreamStateConverter(ABC):
    START_KEY = "start"
    END_KEY = "end"

    @abstractmethod
    def deserialize(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Perform any transformations needed for compatibility with the converter.
        """
        ...

    @staticmethod
    def is_state_message_compatible(state: MutableMapping[str, Any]) -> bool:
        return bool(state) and state.get("state_type") in [t.value for t in ConcurrencyCompatibleStateType]

    @abstractmethod
    def convert_from_sequential_state(
        self,
        cursor_field: "CursorField",
        stream_state: MutableMapping[str, Any],
        start: Any,
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
    def convert_to_sequential_state(self, cursor_field: "CursorField", stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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
