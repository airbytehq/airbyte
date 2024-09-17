#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import InitVar, dataclass, field
from datetime import timedelta
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from isodate import Duration, duration_isoformat, parse_duration


@dataclass
class DatetimeBasedCursor(DeclarativeCursor):
    """
    Slices the stream over a datetime range and create a state with format {<cursor_field>: <datetime> }

    Given a start time, end time, a step function, and an optional lookback window,
    the stream slicer will partition the date range from start time - lookback window to end time.

    The step function is defined as a string of the form ISO8601 duration

    The timestamp format accepts the same format codes as datetime.strfptime, which are
    all the format codes required by the 1989 C standard.
    Full list of accepted format codes: https://man7.org/linux/man-pages/man3/strftime.3.html

    Attributes:
        start_datetime (Union[MinMaxDatetime, str]): the datetime that determines the earliest record that should be synced
        end_datetime (Optional[Union[MinMaxDatetime, str]]): the datetime that determines the last record that should be synced
        cursor_field (Union[InterpolatedString, str]): record's cursor field
        datetime_format (str): format of the datetime
        step (Optional[str]): size of the timewindow (ISO8601 duration)
        cursor_granularity (Optional[str]): smallest increment the datetime_format has (ISO 8601 duration) that will be used to ensure that the start of a slice does not overlap with the end of the previous one
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
    _highest_observed_cursor_field_value: Optional[str] = field(
        repr=False, default=None
    )  # tracks the latest observed datetime, which may not be safe to emit in the case of out-of-order records
    _cursor: Optional[str] = field(
        repr=False, default=None
    )  # tracks the latest observed datetime that is appropriate to emit as stream state
    end_datetime: Optional[Union[MinMaxDatetime, str]] = None
    step: Optional[Union[InterpolatedString, str]] = None
    cursor_granularity: Optional[str] = None
    start_time_option: Optional[RequestOption] = None
    end_time_option: Optional[RequestOption] = None
    partition_field_start: Optional[str] = None
    partition_field_end: Optional[str] = None
    lookback_window: Optional[Union[InterpolatedString, str]] = None
    message_repository: Optional[MessageRepository] = None
    is_compare_strictly: Optional[bool] = False
    cursor_datetime_formats: List[str] = field(default_factory=lambda: [])

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if (self.step and not self.cursor_granularity) or (not self.step and self.cursor_granularity):
            raise ValueError(
                f"If step is defined, cursor_granularity should be as well and vice-versa. "
                f"Right now, step is `{self.step}` and cursor_granularity is `{self.cursor_granularity}`"
            )
        self._start_datetime = MinMaxDatetime.create(self.start_datetime, parameters)
        self._end_datetime = None if not self.end_datetime else MinMaxDatetime.create(self.end_datetime, parameters)

        self._timezone = datetime.timezone.utc
        self._interpolation = JinjaInterpolation()

        self._step = (
            self._parse_timedelta(InterpolatedString.create(self.step, parameters=parameters).eval(self.config))
            if self.step
            else datetime.timedelta.max
        )
        self._cursor_granularity = self._parse_timedelta(self.cursor_granularity)
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)
        self._lookback_window = InterpolatedString.create(self.lookback_window, parameters=parameters) if self.lookback_window else None
        self._partition_field_start = InterpolatedString.create(self.partition_field_start or "start_time", parameters=parameters)
        self._partition_field_end = InterpolatedString.create(self.partition_field_end or "end_time", parameters=parameters)
        self._parser = DatetimeParser()

        # If datetime format is not specified then start/end datetime should inherit it from the stream slicer
        if not self._start_datetime.datetime_format:
            self._start_datetime.datetime_format = self.datetime_format
        if self._end_datetime and not self._end_datetime.datetime_format:
            self._end_datetime.datetime_format = self.datetime_format

        if not self.cursor_datetime_formats:
            self.cursor_datetime_formats = [self.datetime_format]

    def get_stream_state(self) -> StreamState:
        return {self.cursor_field.eval(self.config): self._cursor} if self._cursor else {}  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Cursors are not initialized with their state. As state is needed in order to function properly, this method should be called
        before calling anything else

        :param stream_state: The state of the stream as returned by get_stream_state
        """
        self._cursor = stream_state.get(self.cursor_field.eval(self.config)) if stream_state else None  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Register a record with the cursor; the cursor instance can then use it to manage the state of the in-progress stream read.

        :param stream_slice: The current slice, which may or may not contain the most recently observed record
        :param record: the most recently-read record, which the cursor can use to update the stream state. Outwardly-visible changes to the
          stream state may need to be deferred depending on whether the source reliably orders records by the cursor field.
        """
        record_cursor_value = record.get(self.cursor_field.eval(self.config))  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__
        # if the current record has no cursor value, we cannot meaningfully update the state based on it, so there is nothing more to do
        if not record_cursor_value:
            return

        start_field = self._partition_field_start.eval(self.config)
        end_field = self._partition_field_end.eval(self.config)
        is_highest_observed_cursor_value = not self._highest_observed_cursor_field_value or self.parse_date(
            record_cursor_value
        ) > self.parse_date(self._highest_observed_cursor_field_value)
        if (
            self._is_within_daterange_boundaries(record, stream_slice.get(start_field), stream_slice.get(end_field))  # type: ignore # we know that stream_slices for these cursors will use a string representing an unparsed date
            and is_highest_observed_cursor_value
        ):
            self._highest_observed_cursor_field_value = record_cursor_value

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        if stream_slice.partition:
            raise ValueError(f"Stream slice {stream_slice} should not have a partition. Got {stream_slice.partition}.")
        cursor_value_str_by_cursor_value_datetime = dict(
            map(
                # we need to ensure the cursor value is preserved as is in the state else the CATs might complain of something like
                # 2023-01-04T17:30:19.000Z' <= '2023-01-04T17:30:19.000000Z'
                lambda datetime_str: (self.parse_date(datetime_str), datetime_str),  # type: ignore # because of the filter on the next line, this will only be called with a str
                filter(lambda item: item, [self._cursor, self._highest_observed_cursor_field_value]),
            )
        )
        self._cursor = (
            cursor_value_str_by_cursor_value_datetime[max(cursor_value_str_by_cursor_value_datetime.keys())]
            if cursor_value_str_by_cursor_value_datetime
            else None
        )

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Partition the daterange into slices of size = step.

        The start of the window is the minimum datetime between start_datetime - lookback_window and the stream_state's datetime
        The end of the window is the minimum datetime between the start of the window and end_datetime.

        :return:
        """
        end_datetime = self.select_best_end_datetime()
        start_datetime = self._calculate_earliest_possible_value(self.select_best_end_datetime())
        return self._partition_daterange(start_datetime, end_datetime, self._step)

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        # Datetime based cursors operate over slices made up of datetime ranges. Stream state is based on the progress
        # through each slice and does not belong to a specific slice. We just return stream state as it is.
        return self.get_stream_state()

    def _calculate_earliest_possible_value(self, end_datetime: datetime.datetime) -> datetime.datetime:
        lookback_delta = self._parse_timedelta(self._lookback_window.eval(self.config) if self._lookback_window else "P0D")
        earliest_possible_start_datetime = min(self._start_datetime.get_datetime(self.config), end_datetime)
        cursor_datetime = self._calculate_cursor_datetime_from_state(self.get_stream_state())
        return max(earliest_possible_start_datetime, cursor_datetime) - lookback_delta

    def select_best_end_datetime(self) -> datetime.datetime:
        """
        Returns the optimal end datetime.
        This method compares the current datetime with a pre-configured end datetime
        and returns the earlier of the two. If no pre-configured end datetime is set,
        the current datetime is returned.

        :return datetime.datetime: The best end datetime, which is either the current datetime or the pre-configured end datetime, whichever is earlier.
        """
        now = datetime.datetime.now(tz=self._timezone)
        if not self._end_datetime:
            return now
        return min(self._end_datetime.get_datetime(self.config), now)

    def _calculate_cursor_datetime_from_state(self, stream_state: Mapping[str, Any]) -> datetime.datetime:
        if self.cursor_field.eval(self.config, stream_state=stream_state) in stream_state:  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__
            return self.parse_date(stream_state[self.cursor_field.eval(self.config)])  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__
        return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

    def _format_datetime(self, dt: datetime.datetime) -> str:
        return self._parser.format(dt, self.datetime_format)

    def _partition_daterange(
        self, start: datetime.datetime, end: datetime.datetime, step: Union[datetime.timedelta, Duration]
    ) -> List[StreamSlice]:
        start_field = self._partition_field_start.eval(self.config)
        end_field = self._partition_field_end.eval(self.config)
        dates = []

        while self._is_within_date_range(start, end):
            next_start = self._evaluate_next_start_date_safely(start, step)
            end_date = self._get_date(next_start - self._cursor_granularity, end, min)
            dates.append(
                StreamSlice(
                    partition={}, cursor_slice={start_field: self._format_datetime(start), end_field: self._format_datetime(end_date)}
                )
            )
            start = next_start
        return dates

    def _is_within_date_range(self, start: datetime.datetime, end: datetime.datetime) -> bool:
        if self.is_compare_strictly:
            return start < end
        return start <= end

    def _evaluate_next_start_date_safely(self, start: datetime.datetime, step: datetime.timedelta) -> datetime.datetime:
        """
        Given that we set the default step at datetime.timedelta.max, we will generate an OverflowError when evaluating the next start_date
        This method assumes that users would never enter a step that would generate an overflow. Given that would be the case, the code
        would have broken anyway.
        """
        try:
            return start + step
        except OverflowError:
            return datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

    def _get_date(
        self,
        cursor_value: datetime.datetime,
        default_date: datetime.datetime,
        comparator: Callable[[datetime.datetime, datetime.datetime], datetime.datetime],
    ) -> datetime.datetime:
        cursor_date = cursor_value or default_date
        return comparator(cursor_date, default_date)

    def parse_date(self, date: str) -> datetime.datetime:
        for datetime_format in self.cursor_datetime_formats + [self.datetime_format]:
            try:
                return self._parser.parse(date, datetime_format)
            except ValueError:
                pass
        raise ValueError(f"No format in {self.cursor_datetime_formats} matching {date}")

    @classmethod
    def _parse_timedelta(cls, time_str: Optional[str]) -> Union[datetime.timedelta, Duration]:
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

    def _get_request_options(self, option_type: RequestOptionType, stream_slice: Optional[StreamSlice]) -> Mapping[str, Any]:
        options: MutableMapping[str, Any] = {}
        if not stream_slice:
            return options
        if self.start_time_option and self.start_time_option.inject_into == option_type:
            options[self.start_time_option.field_name.eval(config=self.config)] = stream_slice.get(  # type: ignore # field_name is always casted to an interpolated string
                self._partition_field_start.eval(self.config)
            )
        if self.end_time_option and self.end_time_option.inject_into == option_type:
            options[self.end_time_option.field_name.eval(config=self.config)] = stream_slice.get(self._partition_field_end.eval(self.config))  # type: ignore # field_name is always casted to an interpolated string
        return options

    def should_be_synced(self, record: Record) -> bool:
        cursor_field = self.cursor_field.eval(self.config)  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__
        record_cursor_value = record.get(cursor_field)
        if not record_cursor_value:
            self._send_log(
                Level.WARN,
                f"Could not find cursor field `{cursor_field}` in record. The incremental sync will assume it needs to be synced",
            )
            return True
        latest_possible_cursor_value = self.select_best_end_datetime()
        earliest_possible_cursor_value = self._calculate_earliest_possible_value(latest_possible_cursor_value)
        return self._is_within_daterange_boundaries(record, earliest_possible_cursor_value, latest_possible_cursor_value)

    def _is_within_daterange_boundaries(
        self, record: Record, start_datetime_boundary: Union[datetime.datetime, str], end_datetime_boundary: Union[datetime.datetime, str]
    ) -> bool:
        cursor_field = self.cursor_field.eval(self.config)  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__
        record_cursor_value = record.get(cursor_field)
        if not record_cursor_value:
            self._send_log(
                Level.WARN,
                f"Could not find cursor field `{cursor_field}` in record. The record will not be considered when emitting sync state",
            )
            return False
        if isinstance(start_datetime_boundary, str):
            start_datetime_boundary = self.parse_date(start_datetime_boundary)
        if isinstance(end_datetime_boundary, str):
            end_datetime_boundary = self.parse_date(end_datetime_boundary)
        return start_datetime_boundary <= self.parse_date(record_cursor_value) <= end_datetime_boundary

    def _send_log(self, level: Level, message: str) -> None:
        if self.message_repository:
            self.message_repository.emit_message(
                AirbyteMessage(
                    type=Type.LOG,
                    log=AirbyteLogMessage(level=level, message=message),
                )
            )

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        cursor_field = self.cursor_field.eval(self.config)  # type: ignore  # cursor_field is converted to an InterpolatedString in __post_init__
        first_cursor_value = first.get(cursor_field)
        second_cursor_value = second.get(cursor_field)
        if first_cursor_value and second_cursor_value:
            return self.parse_date(first_cursor_value) >= self.parse_date(second_cursor_value)
        elif first_cursor_value:
            return True
        else:
            return False

    def set_runtime_lookback_window(self, lookback_window_in_seconds: int) -> None:
        """
        Updates the lookback window based on a given number of seconds if the new duration
        is greater than the currently configured lookback window.

        :param lookback_window_in_seconds: The lookback duration in seconds to potentially update to.
        """
        runtime_lookback_window = duration_isoformat(timedelta(seconds=lookback_window_in_seconds))
        config_lookback = parse_duration(self._lookback_window.eval(self.config) if self._lookback_window else "P0D")

        # Check if the new runtime lookback window is greater than the current config lookback
        if parse_duration(runtime_lookback_window) > config_lookback:
            self._lookback_window = InterpolatedString.create(runtime_lookback_window, parameters={})
