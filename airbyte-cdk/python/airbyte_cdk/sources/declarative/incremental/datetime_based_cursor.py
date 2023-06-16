#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from isodate import Duration, parse_duration


@dataclass
class DatetimeBasedCursor(StreamSlicer):
    """
    Slices the stream over a datetime range.

    Given a start time, end time, a step function, and an optional lookback window,
    the stream slicer will partition the date range from start time - lookback window to end time.

    The step function is defined as a string of the form ISO8601 duration

    The timestamp format accepts the same format codes as datetime.strfptime, which are
    all the format codes required by the 1989 C standard.
    Full list of accepted format codes: https://man7.org/linux/man-pages/man3/strftime.3.html

    Attributes:
        start_datetime (Union[MinMaxDatetime, str]): the datetime that determines the earliest record that should be synced
        end_datetime (Optional[Union[MinMaxDatetime, str]]): the datetime that determines the last record that should be synced
        step (str): size of the timewindow (ISO8601 duration)
        cursor_field (Union[InterpolatedString, str]): record's cursor field
        datetime_format (str): format of the datetime
        cursor_granularity (str): smallest increment the datetime_format has (ISO 8601 duration) that will be used to ensure that the start of a slice does not overlap with the end of the previous one
        config (Config): connection config
        start_time_option (Optional[RequestOption]): request option for start time
        end_time_option (Optional[RequestOption]): request option for end time
        partition_field_start (Optional[str]): partition start time field
        partition_field_end (Optional[str]): stream slice end time field
        lookback_window (Optional[InterpolatedString]): how many days before start_datetime to read data for (ISO8601 duration)
    """

    start_datetime: Union[MinMaxDatetime, str]
    cursor_field: Union[InterpolatedString, str]
    datetime_format: str
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    _cursor: dict = field(repr=False, default=None)  # tracks current datetime
    _cursor_end: dict = field(repr=False, default=None)  # tracks end of current stream slice
    end_datetime: Optional[Union[MinMaxDatetime, str]] = None
    step: Optional[Union[InterpolatedString, str]] = None
    cursor_granularity: Optional[str] = None
    start_time_option: Optional[RequestOption] = None
    end_time_option: Optional[RequestOption] = None
    partition_field_start: Optional[str] = None
    partition_field_end: Optional[str] = None
    lookback_window: Optional[Union[InterpolatedString, str]] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        if (self.step and not self.cursor_granularity) or (not self.step and self.cursor_granularity):
            raise ValueError(
                f"If step is defined, cursor_granularity should be as well and vice-versa. "
                f"Right now, step is `{self.step}` and cursor_granularity is `{self.cursor_granularity}`"
            )
        if not isinstance(self.start_datetime, MinMaxDatetime):
            self.start_datetime = MinMaxDatetime(self.start_datetime, parameters)
        if self.end_datetime and not isinstance(self.end_datetime, MinMaxDatetime):
            self.end_datetime = MinMaxDatetime(self.end_datetime, parameters)

        self._timezone = datetime.timezone.utc
        self._interpolation = JinjaInterpolation()

        self._step = (
            self._parse_timedelta(InterpolatedString.create(self.step, parameters=parameters).eval(self.config))
            if self.step
            else datetime.timedelta.max
        )
        self._cursor_granularity = self._parse_timedelta(self.cursor_granularity)
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)
        self.lookback_window = InterpolatedString.create(self.lookback_window, parameters=parameters)
        self.partition_field_start = InterpolatedString.create(self.partition_field_start or "start_time", parameters=parameters)
        self.partition_field_end = InterpolatedString.create(self.partition_field_end or "end_time", parameters=parameters)
        self._parser = DatetimeParser()

        # If datetime format is not specified then start/end datetime should inherit it from the stream slicer
        if not self.start_datetime.datetime_format:
            self.start_datetime.datetime_format = self.datetime_format
        if self.end_datetime and not self.end_datetime.datetime_format:
            self.end_datetime.datetime_format = self.datetime_format

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field.eval(self.config): self._cursor} if self._cursor else {}

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        """
        Update the cursor value to the max datetime between the last record, the start of the stream_slice, and the current cursor value.
        Update the cursor_end value with the stream_slice's end time.

        :param stream_slice: current stream slice
        :param last_record: last record read
        :return: None
        """
        stream_slice_value = stream_slice.get(self.cursor_field.eval(self.config))
        stream_slice_value_end = stream_slice.get(self.partition_field_end.eval(self.config))
        last_record_value = last_record.get(self.cursor_field.eval(self.config)) if last_record else None
        cursor = None
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
        if self.partition_field_end:
            self._cursor_end = stream_slice_value_end

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        """
        Partition the daterange into slices of size = step.

        The start of the window is the minimum datetime between start_datetime - lookback_window and the stream_state's datetime
        The end of the window is the minimum datetime between the start of the window and end_datetime.

        :param sync_mode:
        :param stream_state: current stream state. If set, the start_date will be the day following the stream_state.
        :return:
        """
        stream_state = stream_state or {}
        kwargs = {"stream_state": stream_state}
        end_datetime = self._select_best_end_datetime(kwargs)
        lookback_delta = self._parse_timedelta(self.lookback_window.eval(self.config, **kwargs) if self.lookback_window else "P0D")

        earliest_possible_start_datetime = min(self.start_datetime.get_datetime(self.config, **kwargs), end_datetime)
        cursor_datetime = self._calculate_cursor_datetime_from_state(stream_state)
        start_datetime = max(earliest_possible_start_datetime, cursor_datetime) - lookback_delta

        return self._partition_daterange(start_datetime, end_datetime, self._step)

    def _select_best_end_datetime(self, kwargs):
        now = datetime.datetime.now(tz=self._timezone)
        if not self.end_datetime:
            return now
        return min(self.end_datetime.get_datetime(self.config, **kwargs), now)

    def _calculate_cursor_datetime_from_state(self, stream_state: Mapping[str, Any]) -> datetime.datetime:
        if self.cursor_field.eval(self.config, stream_state=stream_state) in stream_state:
            return self.parse_date(stream_state[self.cursor_field.eval(self.config)])
        return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

    def _format_datetime(self, dt: datetime.datetime):
        return self._parser.format(dt, self.datetime_format)

    def _partition_daterange(self, start: datetime.datetime, end: datetime.datetime, step: Union[datetime.timedelta, Duration]):
        start_field = self.partition_field_start.eval(self.config)
        end_field = self.partition_field_end.eval(self.config)
        dates = []
        while start <= end:
            next_start = self._evaluate_next_start_date_safely(start, step)
            end_date = self._get_date(next_start - self._cursor_granularity, end, min)
            dates.append({start_field: self._format_datetime(start), end_field: self._format_datetime(end_date)})
            start = next_start
        return dates

    def _evaluate_next_start_date_safely(self, start, step):
        """
        Given that we set the default step at datetime.timedelta.max, we will generate an OverflowError when evaluating the next start_date
        This method assumes that users would never enter a step that would generate an overflow. Given that would be the case, the code
        would have broken anyway.
        """
        try:
            return start + step
        except OverflowError:
            return datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

    def _get_date(self, cursor_value, default_date: datetime.datetime, comparator) -> datetime.datetime:
        cursor_date = cursor_value or default_date
        return comparator(cursor_date, default_date)

    def parse_date(self, date: str) -> datetime.datetime:
        return self._parser.parse(date, self.datetime_format)

    @classmethod
    def _parse_timedelta(cls, time_str) -> Union[datetime.timedelta, Duration]:
        """
        :return Parses an ISO 8601 durations into datetime.timedelta or Duration objects.
        """
        if not time_str:
            return datetime.timedelta(0)
        return parse_duration(time_str)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.body_json, stream_slice)

    def request_kwargs(self) -> Mapping[str, Any]:
        # Never update kwargs
        return {}

    def _get_request_options(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        options = {}
        if self.start_time_option and self.start_time_option.inject_into == option_type:
            options[self.start_time_option.field_name] = stream_slice.get(self.partition_field_start.eval(self.config))
        if self.end_time_option and self.end_time_option.inject_into == option_type:
            options[self.end_time_option.field_name] = stream_slice.get(self.partition_field_end.eval(self.config))
        return options
