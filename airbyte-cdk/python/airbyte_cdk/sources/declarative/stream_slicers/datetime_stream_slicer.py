#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import re
from typing import Any, Iterable, Mapping, Optional, Union

import dateutil
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config


class DatetimeStreamSlicer(StreamSlicer):
    timedelta_regex = re.compile(
        r"((?P<weeks>[\.\d]+?)w)?"
        r"((?P<days>[\.\d]+?)d)?"
        r"((?P<hours>[\.\d]+?)h)?"
        r"((?P<minutes>[\.\d]+?)m)?"
        r"((?P<seconds>[\.\d]+?)s)?"
        r"((?P<microseconds>[\.\d]+?)ms)?"
        r"((?P<milliseconds>[\.\d]+?)us)?$"
    )

    def __init__(
        self,
        start_datetime: MinMaxDatetime,
        end_datetime: MinMaxDatetime,
        step: str,
        cursor_field: InterpolatedString,
        datetime_format: str,
        config: Config,
        start_time_option: Optional[RequestOption] = None,
        end_time_option: Optional[RequestOption] = None,
        stream_state_field_start: Optional[str] = None,
        stream_state_field_end: Optional[str] = None,
        lookback_window: Optional[InterpolatedString] = None,
    ):
        """

        :param start_datetime:
        :param end_datetime:
        :param step:
        :param cursor_field: record's cursor field
        :param datetime_format:
        :param config:
        :param start_time_option: request option for start time
        :param end_time_option: request option for end time
        :param stream_state_field_start: stream slice start time field
        :param stream_state_field_end: stream slice end time field
        :param lookback_window:
        """
        self._timezone = datetime.timezone.utc
        self._interpolation = JinjaInterpolation()

        self._datetime_format = datetime_format
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime
        self._step = self._parse_timedelta(step)
        self._config = config
        self._cursor_field = cursor_field
        if isinstance(self._cursor_field, str):
            self._cursor_field = InterpolatedString(self._cursor_field)
        self._start_time_option = start_time_option
        self._end_time_option = end_time_option
        self._stream_slice_field_start = stream_state_field_start or "start_date"
        if isinstance(self._stream_slice_field_start, str):
            self._stream_slice_field_start = InterpolatedString(string=self._stream_slice_field_start)
        if stream_state_field_end and isinstance(stream_state_field_end, str):
            self._stream_slice_field_end = InterpolatedString(stream_state_field_end)
        elif stream_state_field_end:
            self._stream_slice_field_end = stream_state_field_end
        else:
            self._stream_slice_field_end = InterpolatedString("end_date")
        self._cursor = None
        self._cursor_end = None
        self._lookback_window = lookback_window

        # If datetime format is not specified then start/end datetime should inherit it from the stream slicer
        if not self._start_datetime.datetime_format:
            self._start_datetime.datetime_format = self._datetime_format
        if not self._end_datetime.datetime_format:
            self._end_datetime.datetime_format = self._datetime_format

        if self._start_time_option and self._start_time_option.pass_by == RequestOptionType.path:
            raise ValueError("Start time cannot be passed by path")
        if self._end_time_option and self._end_time_option.pass_by == RequestOptionType.path:
            raise ValueError("End time cannot be passed by path")

    def get_stream_state(self) -> Optional[Mapping[str, Any]]:
        return {self._cursor_field.eval(self._config): self._cursor} if self._cursor else None

    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]] = None):
        stream_slice_value = stream_slice.get(self._cursor_field.eval(self._config))
        stream_slice_value_end = stream_slice.get(self._stream_slice_field_end.eval(self._config))
        last_record_value = last_record.get(self._cursor_field.eval(self._config)) if last_record else None
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
        if self._stream_slice_field_end:
            self._cursor_end = stream_slice_value_end

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        # Evaluate and compare start_date, end_date, and cursor_value based on configs and runtime state
        stream_state = stream_state or {}
        kwargs = {"stream_state": stream_state}
        end_datetime = min(self._end_datetime.get_datetime(self._config, **kwargs), datetime.datetime.now(tz=datetime.timezone.utc))
        lookback_delta = self._parse_timedelta(self._lookback_window.eval(self._config, **kwargs) if self._lookback_window else "0d")
        start_datetime = self._start_datetime.get_datetime(self._config, **kwargs) - lookback_delta
        start_datetime = min(start_datetime, end_datetime)
        if self._cursor_field.eval(self._config, stream_state=stream_state) in stream_state:
            cursor_datetime = self.parse_date(stream_state[self._cursor_field.eval(self._config)])
        else:
            cursor_datetime = start_datetime
        start_datetime = max(cursor_datetime, start_datetime)

        dates = self._partition_daterange(start_datetime, end_datetime, self._step)
        state_date = stream_state.get(self._cursor_field.eval(self._config, stream_state=stream_state))
        if state_date:
            dates_later_than_state = [d for d in dates if d[self._stream_slice_field_start.eval(self._config)] > state_date]
        else:
            dates_later_than_state = dates
        return dates_later_than_state

    def _format_datetime(self, dt: datetime.datetime):
        if self._datetime_format == "timestamp":
            return dt.timestamp()
        else:
            return dt.strftime(self._datetime_format)

    def _partition_daterange(self, start, end, step: datetime.timedelta):
        start_field = self._stream_slice_field_start.eval(self._config) or "start_time"
        end_field = self._stream_slice_field_end.eval(self._config) or "end_time"
        dates = []
        while start <= end:
            end_date = self._get_date(start + step - datetime.timedelta(days=1), end, min)
            dates.append({start_field: self._format_datetime(start), end_field: self._format_datetime(end_date)})
            start += step
        return dates

    def _get_date(self, cursor_value, default_date: datetime.datetime, comparator) -> datetime.datetime:
        cursor_date = self.parse_date(cursor_value or default_date)
        return comparator(cursor_date, default_date)

    def parse_date(self, date: Any) -> datetime:
        if date and isinstance(date, str):
            if self.is_int(date):
                return datetime.datetime.fromtimestamp(int(date)).replace(tzinfo=self._timezone)
            else:
                return dateutil.parser.parse(date).replace(tzinfo=self._timezone)
        elif isinstance(date, int):
            return datetime.datetime.fromtimestamp(int(date)).replace(tzinfo=self._timezone)
        return date

    def is_int(self, s) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False

    @classmethod
    def _parse_timedelta(cls, time_str):
        """
        Parse a time string e.g. (2h13m) into a timedelta object.
        Modified from virhilo's answer at https://stackoverflow.com/a/4628148/851699
        :param time_str: A string identifying a duration. (eg. 2h13m)
        :return datetime.timedelta: A datetime.timedelta object
        """
        parts = cls.timedelta_regex.match(time_str)

        assert parts is not None

        time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
        return datetime.timedelta(**time_params)

    def request_params(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.request_parameter)

    def request_headers(self) -> Mapping[str, Any]:
        return self._get_request_options(RequestOptionType.header)

    def request_body_data(self) -> Optional[Union[Mapping, str]]:
        return self._get_request_options(RequestOptionType.body_data)

    def request_body_json(self) -> Optional[Mapping]:
        return self._get_request_options(RequestOptionType.body_json)

    def _get_request_options(self, option_type):
        options = {}
        if self._start_time_option and self._start_time_option.pass_by == option_type:
            if self._cursor:
                options[self._start_time_option.field_name] = self._cursor
        if self._end_time_option and self._end_time_option.pass_by == option_type:
            options[self._end_time_option.field_name] = self._cursor_end
        return options
