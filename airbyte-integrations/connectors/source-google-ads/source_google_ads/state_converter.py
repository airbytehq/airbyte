# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, MutableMapping, Optional, Tuple, Union

import pendulum
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converters.abstract_stream_state_converter import ConcurrencyCompatibleStateType
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter
from source_google_ads.models import CustomerModel


class GadsStateConverter(EpochValueConcurrentStreamStateConverter):
    zero_value = "0001-01-01"

    def __init__(self, customers: list[CustomerModel]):
        self.customers = customers

    def increment(self, timestamp: datetime) -> datetime:
        return timestamp + timedelta(days=1)

    def output_format(self, timestamp: date) -> str:
        return str(timestamp)

    def parse_timestamp(self, timestamp: Union[date, str]) -> date:
        if isinstance(timestamp, date):
            return timestamp
        dt_object = pendulum.parse(timestamp)
        return dt_object.date()

    def deserialize(self, state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        for stream_slice in state.get("slices", []):
            stream_slice[self.START_KEY] = self.parse_timestamp(stream_slice[self.START_KEY])
            stream_slice[self.END_KEY] = self.parse_timestamp(stream_slice[self.END_KEY])
        return state

    def convert_from_sequential_state(
        self, cursor_field: CursorField, stream_state: MutableMapping[str, Any], start: datetime
    ) -> Tuple[MutableMapping[str, date], MutableMapping[str, Any]]:
        """
        Convert the state message to the format required by the GoogleAdsCursor.

        e.g.
        {
            {
                "1234567890": "state_type": ConcurrencyCompatibleStateType.date_range.value,
                "slices": [
                    {"start": "2021-01-18", "end": "2021-01-18"}
                ]
            }
        }
        """
        sync_start = self._get_sync_start(cursor_field, stream_state, start)
        concurrent_state = {}
        for customer_id, customer_state in stream_state.items():
            if customer_id not in sync_start:
                sync_start[customer_id] = self.parse_timestamp(start)
            if self.is_state_message_compatible(customer_state):
                concurrent_state[customer_id] = stream_state
            else:
                slices = [{self.START_KEY: sync_start[customer_id], self.END_KEY: sync_start[customer_id]}]
                concurrent_state[customer_id] = {
                    "state_type": ConcurrencyCompatibleStateType.date_range.value,
                    "slices": slices,
                    "legacy": stream_state.get(customer_id, {}).get("legacy", {}),
                }

        # Create a slice to represent the records synced during prior syncs.
        # The start and end are the same to avoid confusion as to whether the records for this slice
        # were actually synced

        for customer in self.customers:
            if customer.id not in concurrent_state:
                slices = [{self.START_KEY: sync_start[customer.id], self.END_KEY: sync_start[customer.id]}]
                concurrent_state[customer.id] = {
                    "state_type": ConcurrencyCompatibleStateType.date_range.value,
                    "slices": slices,
                    "legacy": stream_state.get(customer.id, {}).get("legacy", {}),
                }
        return sync_start, concurrent_state

    def _get_sync_start(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any], start: Optional[Any]) -> dict[str, date]:
        sync_start = self.parse_timestamp(start) if start is not None else self.zero_value
        result = {}
        for customer in self.customers:
            state = stream_state.get(customer.id, {})
            prev_sync_low_water_mark = (
                self.parse_timestamp(state[cursor_field.cursor_field_key]) if cursor_field.cursor_field_key in state else None
            )
            if prev_sync_low_water_mark and prev_sync_low_water_mark >= sync_start:
                result[customer.id] = prev_sync_low_water_mark
            else:
                result[customer.id] = sync_start
        return result

    def convert_to_sequential_state(self, cursor_field: CursorField, stream_state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Convert the state message from the concurrency-compatible format to the stream's original format.

        e.g.
        {
            "1234567890": {
                "segments.date": "2024-04-05"
            }
        }
        """
        new_state = {}
        for customer_id, customer_state in stream_state.items():
            if self.is_state_message_compatible(customer_state):
                legacy_state = customer_state.get("legacy", {})
                latest_complete_time = self._get_latest_complete_time(customer_state.get("slices", []))
                if latest_complete_time is not None:
                    legacy_state.update({cursor_field.cursor_field_key: self.output_format(latest_complete_time)})
                new_state[customer_id] = legacy_state or {}
            else:
                new_state[customer_id] = customer_state
        return new_state

    @classmethod
    def get_end_provider(cls) -> Callable[[], datetime.date]:
        return lambda: datetime.now(timezone.utc).date()
