#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import re
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


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

    # FIXME: start_time, end_time, and step should be datetime and timedelta?
    # FIXME: timezone should be declarative?
    def __init__(
        self,
        start_time: InterpolatedString,
        end_time: InterpolatedString,
        step,
        cursor_value: InterpolatedString,
        datetime_format,
        config,
    ):
        self._timezone = datetime.timezone.utc
        self._interpolation = JinjaInterpolation()
        self._datetime_format = datetime_format
        self._start_time = self.parse_date(start_time.eval(config))
        self._end_time = self.parse_date(end_time.eval(config))
        self._end_time = min(self._end_time, datetime.datetime.now(tz=datetime.timezone.utc))
        self._start_time = min(self._start_time, self._end_time)
        self._step = self._parse_timedelta(step)
        self._config = config
        self._cursor_value = cursor_value

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}

        cursor_value = self._cursor_value.eval(self._config, **{"stream_state": stream_state})
        start_date = self._get_date(self.parse_date(cursor_value), self._start_time, max)
        if not self.is_start_date_valid(start_date):
            self._end_time = start_date
        return self._partition_daterange(start_date, self._end_time, self._step)

    def _partition_daterange(self, start, end, step: datetime.timedelta):
        dates = []
        while start <= end:
            end_date = self._get_date(start + step - datetime.timedelta(days=1), end, min)
            dates.append({"start_date": start.strftime(self._datetime_format), "end_date": end_date.strftime(self._datetime_format)})
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
                return datetime.datetime.strptime(date, self._datetime_format).replace(tzinfo=self._timezone)
        return date

    def is_start_date_valid(self, start_date: datetime) -> bool:
        return start_date <= self._end_time

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
