#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from dataclasses import dataclass

import pendulum
from airbyte_cdk.sources.declarative.stream_slicers import DatetimeStreamSlicer


@dataclass
class CustomDatetimeStreamSlicer(DatetimeStreamSlicer):
    """
    This customization helps us to avoid problems when we meet different datetime formats in a single stream.
    For example if a stream "S" has a `date_created` field filled with "2021-01-01T00:00:00.000000+00:00" value in record 1,
    but at the same time the value of the same field is "2021-01-01T00:00:00+00:00 in record 2,
    then it is not enough to specify only one format in the `datetime_format` option.
    """

    def _format_datetime(self, dt: datetime.datetime) -> str:
        return pendulum.datetime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tz=dt.tzinfo or self._timezone,
        ).to_iso8601_string()

    def parse_date(self, date: str) -> datetime.datetime:
        return pendulum.parse(date, tz=self._timezone)
