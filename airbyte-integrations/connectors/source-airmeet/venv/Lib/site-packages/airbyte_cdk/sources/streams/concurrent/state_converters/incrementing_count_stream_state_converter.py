#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Callable, MutableMapping, Optional, Tuple

from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import (
    AbstractStreamStateConverter,
    ConcurrencyCompatibleStateType,
)


class IncrementingCountStreamStateConverter(AbstractStreamStateConverter):
    def _from_state_message(self, value: Any) -> Any:
        return value

    def _to_state_message(self, value: Any) -> Any:
        return value

    @classmethod
    def get_end_provider(cls) -> Callable[[], float]:
        return lambda: float("inf")

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
                {"start": "10", "end": "2021-01-18T21:18:20.000+00:00"},
            ]
        }
        """
        sync_start = self._get_sync_start(cursor_field, stream_state, start)
        if self.is_state_message_compatible(stream_state):
            return sync_start, stream_state

        # Create a slice to represent the records synced during prior syncs.
        # The start and end are the same to avoid confusion as to whether the records for this slice
        # were actually synced
        slices = [
            {
                self.START_KEY: start if start is not None else sync_start,
                self.END_KEY: sync_start,  # this may not be relevant anymore
                self.MOST_RECENT_RECORD_KEY: sync_start,
            }
        ]

        return sync_start, {
            "state_type": ConcurrencyCompatibleStateType.integer.value,
            "slices": slices,
            "legacy": stream_state,
        }

    def parse_value(self, value: int) -> int:
        return value

    @property
    def zero_value(self) -> int:
        return 0

    def increment(self, value: int) -> int:
        return value + 1

    def output_format(self, value: int) -> int:
        return value

    def _get_sync_start(
        self,
        cursor_field: CursorField,
        stream_state: MutableMapping[str, Any],
        start: Optional[int],
    ) -> int:
        sync_start = start if start is not None else self.zero_value
        prev_sync_low_water_mark: Optional[int] = (
            stream_state[cursor_field.cursor_field_key]
            if cursor_field.cursor_field_key in stream_state
            else None
        )
        if prev_sync_low_water_mark and prev_sync_low_water_mark >= sync_start:
            return prev_sync_low_water_mark
        else:
            return sync_start
