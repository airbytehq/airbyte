import datetime
import pendulum

from dataclasses import dataclass, field
from typing import Optional, Iterable, Mapping, Any, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType, RequestOption
from airbyte_cdk.sources.declarative.stream_slicers import SingleSlice
from airbyte_cdk.sources.declarative.types import StreamState, StreamSlice, Record, Config


@dataclass
class SingleStreamSlicer(SingleSlice):
    config:                   Config
    cursor_field:             Union[InterpolatedString, str]
    start_datetime:           Union[MinMaxDatetime, str]
    datetime_format:          str
    start_time_option:        Optional[RequestOption] = None
    start_time_option_tpl:    Optional[str] = "%s"
    stream_state_field_start: Optional[str] = None

    _cursor:                  str = field(repr=False, default="")

    def __post_init__(self, options: Mapping[str, Any]):
        self.cursor_field = InterpolatedString.create(self.cursor_field, options=options)
        self.stream_slice_field_start = InterpolatedString.create(self.stream_state_field_start or "start_time", options=options)

        self._parser = pendulum
        self._timezone = datetime.timezone.utc

        if not isinstance(self.start_datetime, MinMaxDatetime):
            self.start_datetime = MinMaxDatetime(self.start_datetime, options)

        if not self.start_datetime.datetime_format:
            self.start_datetime.datetime_format = self.datetime_format

        if self.start_time_option.field_name:
            self.start_time_option.field_name = InterpolatedString.create(self.start_time_option.field_name, options=options)

        if self.start_time_option and self.start_time_option.inject_into == RequestOptionType.path:
            raise ValueError("Start time cannot be passed by path")

    def _format_datetime(self, dt: datetime.datetime) -> str:
        return self._parser.instance(dt, self._timezone).to_iso8601_string()

    def _parse_date(self, date: str) -> datetime.datetime:
        return self._parser.parse(date)

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field.eval(self.config): self._cursor} if self._cursor else {}

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        stream_slice_value = stream_slice.get(self.cursor_field.eval(self.config))
        last_record_value = last_record.get(self.cursor_field.eval(self.config)) if last_record else None
        if stream_slice_value and last_record_value:
            cursor = max(stream_slice_value, last_record_value)
        elif stream_slice_value:
            cursor = stream_slice_value
        else:
            cursor = last_record_value
        if self._cursor and cursor:
            self._cursor = max(cursor, self._cursor)
        elif cursor:
            self._cursor = cursor

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[StreamSlice]:
        stream_state = stream_state or {}
        start_datetime = self.start_datetime.get_datetime(self.config, **{"stream_state": stream_state})
        if self.cursor_field.eval(self.config, stream_state=stream_state) in stream_state:
            start_datetime = max(self._parse_date(stream_state[self.cursor_field.eval(self.config)]), start_datetime)
        return [
            {self.stream_slice_field_start.eval(self.config): self._format_datetime(start_datetime)}
        ]

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter, stream_slice)

    def _get_request_options(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        options = {}
        if self.start_time_option and self.start_time_option.inject_into == option_type:
            options[self.start_time_option.field_name.eval(self.config)] = self.start_time_option_tpl % stream_slice.get(self.stream_slice_field_start.eval(self.config))
        return options
