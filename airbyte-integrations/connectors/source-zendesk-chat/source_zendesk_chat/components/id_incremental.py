#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.message import MessageRepository


@dataclass
class IdIncrementalCursor(Cursor):
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
    _cursor: Optional[str] = field(repr=False, default=None)
    message_repository: Optional[MessageRepository] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._state: Optional[int] = None
        self._interpolation = JinjaInterpolation()
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)
        self.field_name = InterpolatedString.create(self.field_name, parameters=parameters)

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field.eval(self.config): self._cursor} if self._cursor else {}

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Cursors are not initialized with their state. As state is needed in order to function properly, this method should be called
        before calling anything else

        :param stream_state: The state of the stream as returned by get_stream_state
        """
        
        self._cursor = stream_state.get(self.cursor_field.eval(self.config)) if stream_state else None
        self._state = self._cursor if self._cursor else self._state

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        last_record_cursor_value = most_recent_record.get(self.cursor_field.eval(self.config)) if most_recent_record else None
        self._cursor = last_record_cursor_value if last_record_cursor_value else None
        
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Use a single Slice.
        """
        return [None]

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
            options[self.field_name.eval(self.config)] = self._state
        return options

    def should_be_synced(self, record: Record) -> bool:
        cursor_field = self.cursor_field.eval(self.config)
        record_cursor_value: int = record.get(cursor_field)
        if not record_cursor_value:
            self._send_log(
                Level.WARN,
                f"Could not find cursor field `{cursor_field}` in record. The incremental sync will assume it needs to be synced",
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
        cursor_field = self.cursor_field.eval(self.config)
        first_cursor_value = first.get(cursor_field)
        second_cursor_value = second.get(cursor_field)
        if first_cursor_value and second_cursor_value:
            return first_cursor_value >= second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False
