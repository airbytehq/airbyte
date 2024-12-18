#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.message import MessageRepository


@dataclass
class ZendeskChatIdIncrementalCursor(Cursor):
    """
    Custom Incremental Cursor implementation to provide the ability to pull data using `id`(int) as cursor.
    More info: https://developer.zendesk.com/api-reference/live-chat/chat-api/agents/#parameters

    Attributes:
        config (Config): connection config
        field_name (Union[InterpolatedString, str]): the name of the field which will hold the cursor value for outbound API call
        cursor_field (Union[InterpolatedString, str]): record's cursor field
    """

    config: Config
    cursor_field: Union[InterpolatedString, str]
    field_name: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    _highest_observed_record_cursor_value: Optional[str] = field(
        repr=False, default=None
    )  # tracks the latest observed datetime, which may not be safe to emit in the case of out-of-order records
    _cursor: Optional[str] = field(repr=False, default=None)
    message_repository: Optional[MessageRepository] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._state: Optional[int] = None
        self._start_boundary: int = 0
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters).eval(self.config)
        self.field_name = InterpolatedString.create(self.field_name, parameters=parameters).eval(self.config)

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field: self._cursor} if self._cursor else {}

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Cursors are not initialized with their state. As state is needed in order to function properly, this method should be called
        before calling anything else

        :param stream_state: The state of the stream as returned by get_stream_state
        """

        self._cursor = stream_state.get(self.cursor_field) if stream_state else None
        self._start_boundary = self._cursor if self._cursor else 0
        self._state = self._cursor if self._cursor else self._state

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Register a record with the cursor; the cursor instance can then use it to manage the state of the in-progress stream read.

        :param record: the most recently-read record, which the cursor can use to update the stream state. Outwardly-visible changes to the
          stream state may need to be deferred depending on whether the source reliably orders records by the cursor field.
        """
        record_cursor_value = record.get(self.cursor_field)
        if self._is_within_boundaries(record, self._start_boundary):
            self._highest_observed_record_cursor_value = record_cursor_value if record_cursor_value else self._start_boundary

    def _is_within_boundaries(
        self,
        record: Record,
        start_boundary: int,
    ) -> bool:
        record_cursor_value = record.get(self.cursor_field)
        if not record_cursor_value:
            self._send_log(
                Level.WARN,
                f"Could not find cursor field `{self.cursor_field}` in record. The record will not be considered when emitting sync state",
            )
            return False
        return start_boundary <= record_cursor_value

    def collect_cursor_values(self) -> Mapping[str, Optional[int]]:
        """
        Makes the `cursor_values` using `stream_slice` and `most_recent_record`.
        """
        cursor_values: dict = {
            "state": self._cursor if self._cursor else self._start_boundary,
            "highest_observed_record_value": self._highest_observed_record_cursor_value
            if self._highest_observed_record_cursor_value
            else self._start_boundary,
        }
        # filter out the `NONE` STATE values from the `cursor_values`
        return {key: value for key, value in cursor_values.items()}

    def process_state(self, cursor_values: Optional[dict] = None) -> Optional[int]:
        state_value = cursor_values.get("state") if cursor_values else 0
        highest_observed_value = cursor_values.get("highest_observed_record_value") if cursor_values else 0
        return max(state_value, highest_observed_value)

    def close_slice(self, stream_slice: StreamSlice) -> None:
        cursor_values: dict = self.collect_cursor_values()
        self._cursor = self.process_state(cursor_values) if cursor_values else 0

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Use a single Slice.
        """
        return [StreamSlice(partition={}, cursor_slice={})]

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter, stream_slice)

    def _get_request_options(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        options = {}
        if self._state:
            options[self.field_name] = self._state
        return options

    def should_be_synced(self, record: Record) -> bool:
        record_cursor_value: int = record.get(self.cursor_field)
        if not record_cursor_value:
            self._send_log(
                Level.WARN,
                f"Could not find cursor field `{self.cursor_field}` in record. The incremental sync will assume it needs to be synced",
            )
            return True
        latest_possible_cursor_value = self._cursor if self._cursor else 0
        return latest_possible_cursor_value <= record_cursor_value

    def _send_log(self, level: Level, message: str) -> None:
        if self.message_repository:
            self.message_repository.emit_message(
                AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(level=level, message=message),
                )
            )

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        first_cursor_value = first.get(self.cursor_field)
        second_cursor_value = second.get(self.cursor_field)
        if first_cursor_value and second_cursor_value:
            return first_cursor_value >= second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False
