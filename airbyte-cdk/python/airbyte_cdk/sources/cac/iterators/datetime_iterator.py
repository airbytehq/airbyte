#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
from typing import Any, Iterable, Mapping

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.iterators.iterator import Iterator
from pendulum.tz.timezone import Timezone


class DatetimeIterator(Iterator):

    # FIXME: start_time, end_time, and step should be datetime and timedelta?
    def __init__(self, start_time, end_time, step, timezone: Timezone, vars, config):
        self._start_time = start_time
        self._end_time = end_time
        self._step = step
        self._vars = vars
        self._config = config
        self._timezone = timezone
        # FIXME these need to come from params
        self._cursor_value = "date"
        self._end_cursor = "date_end"

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        cursor_value = stream_state.get(self._cursor_value)
        start_date = self._get_date(self.parse_date(cursor_value), self._start_time, max)
        if not self.is_start_date_valid(start_date):
            self._end_time = start_date
        return self._partition_daterange(start_date, self._end_time, self._step, self._cursor_value, self._end_cursor)

    # FIXME start and end field should come from config
    def _partition_daterange(self, start, end, step: datetime.timedelta, start_field: str, end_field: str):
        dates = []
        print(f"end: {end}")
        while start <= end:
            end_date = self._get_date(start + step, end, min)
            dates.append({start_field: start, end_field: end_date})
            start += step
        return dates

    def _get_date(self, cursor_value, default_date: datetime.datetime, comparator) -> datetime.datetime:
        cursor_date = self.parse_date(cursor_value or default_date)
        return comparator(cursor_date, default_date)

    def parse_date(self, date: Any) -> datetime:
        if date and isinstance(date, str):
            return pendulum.parse(date).replace(tzinfo=self._timezone)

        return date

    def is_start_date_valid(self, start_date: datetime) -> bool:
        return start_date <= self._end_time
