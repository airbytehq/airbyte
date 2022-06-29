#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class MinMaxDate:
    """
    Compares the provided date against optional minimum or maximum times. If date is earlier than
    min_date, then min_date is returned. If date is greater than max_date, then max_date is returned.
    """

    def __init__(
        self,
        date: str,
        datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f%z",
        min_date: str = "",
        max_date: str = "",
    ):
        self._date_interpolator = InterpolatedString(date)
        self._datetime_format = datetime_format
        self._timezone = datetime.timezone.utc
        self._min_date_interpolator = InterpolatedString(min_date) if min_date else None
        self._max_date_interpolator = InterpolatedString(max_date) if max_date else None

    def get_date(self, config, **kwargs) -> datetime.datetime:
        time = datetime.datetime.strptime(self._date_interpolator.eval(config, **kwargs), self._datetime_format).replace(
            tzinfo=self._timezone
        )

        if self._min_date_interpolator:
            min_time = datetime.datetime.strptime(self._min_date_interpolator.eval(config, **kwargs), self._datetime_format).replace(
                tzinfo=self._timezone
            )
            time = max(time, min_time)
        if self._max_date_interpolator:
            max_time = datetime.datetime.strptime(self._max_date_interpolator.eval(config, **kwargs), self._datetime_format).replace(
                tzinfo=self._timezone
            )
            time = min(time, max_time)
        return time
