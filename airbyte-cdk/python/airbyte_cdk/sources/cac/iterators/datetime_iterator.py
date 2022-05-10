#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
from typing import Any, Iterable, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.iterators.iterator import Iterator
from pendulum.tz.timezone import Timezone


class DatetimeIterator(Iterator):

    # FIXME: start_time, end_time, and step should be datetime and timedelta?
    def __init__(self, start_time, end_time, step, timezone: Timezone, cursor_value, datetime_format, vars, config):
        self._timezone = timezone
        self._interpolation = JinjaInterpolation()
        self._datetime_format = datetime_format
        self._start_time = self.parse_date(self._interpolation.eval(start_time["value"], vars, config, None, None))
        if not self._start_time:
            self._start_time = self.parse_date(self._interpolation.eval(start_time["default"], vars, config, None, None))
        self._end_time = self.parse_date(self._interpolation.eval(end_time["value"], vars, config, None, None))
        self._end_time = min(self._end_time, datetime.datetime.now(tz=datetime.timezone.utc))
        self._start_time = min(self._start_time, self._end_time)
        self._step = step
        self._vars = vars
        self._config = config
        self._cursor_value = cursor_value

    # FIXME: this needs an update state method?

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        cursor_value = self._interpolation.eval(self._cursor_value, self._vars, self._config, None, stream_state)
        start_date = self._get_date(self.parse_date(cursor_value), self._start_time, max)
        if not self.is_start_date_valid(start_date):
            self._end_time = start_date
        return self._partition_daterange(start_date, self._end_time, self._step)

    # FIXME start and end field should come from config
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
            return datetime.datetime.strptime(date, self._datetime_format).replace(tzinfo=self._timezone)
        return date

    def is_start_date_valid(self, start_date: datetime) -> bool:
        return start_date <= self._end_time
