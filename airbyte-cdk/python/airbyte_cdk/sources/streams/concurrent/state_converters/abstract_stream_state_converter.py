#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Iterable, List, MutableMapping, Optional

if TYPE_CHECKING:
    from airbyte_cdk.sources.streams.concurrent.cursor import CursorField


class ConcurrencyCompatibleStateType(Enum):
    date_range = "date-range"


class AbstractStreamStateConverter(ABC):
    START_KEY = "start"
    END_KEY = "end"

    def get_concurrent_stream_state(
        self, cursor_field: Optional["CursorField"], state: MutableMapping[str, Any]
    ) -> Optional[MutableMapping[str, Any]]:
        if not cursor_field:
            return None
        if self.is_state_message_compatible(state):
            return self.deserialize(state)
        return self.convert_from_sequential_state(cursor_field, state)

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
        self, cursor_field: "CursorField", stream_state: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        """
        Convert the state message to the format required by the ConcurrentCursor.

        e.g.
        {
            "state_type": ConcurrencyCompatibleStateType.date_range.value,
            "metadata": { … },
            "low_water_mark": 1617030403
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
    def decrement(self, item: Any) -> Any:
        """
        Decrement an item by a single unit.
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

    @abstractmethod
    def is_greater_than(self, item1: Any, item2: Any) -> bool:
        """
        Return True if the first item is greater than the second item.
        """
        ...

    @abstractmethod
    def min(self, *items: Iterable[Any]) -> Any:
        """
        Performs a comparison of the items and returns the min.
        """
        ...

    @abstractmethod
    def max(self, *items: Iterable[Any]) -> Any:
        """
        Performs a comparison of the items and returns the max.
        """
        ...
