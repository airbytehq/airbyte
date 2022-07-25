#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime as dt

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class MinMaxDatetime:
    """
    Compares the provided date against optional minimum or maximum times. If date is earlier than
    min_date, then min_date is returned. If date is greater than max_date, then max_date is returned.
    If neither, the input date is returned.
    """

    def __init__(
        self,
        datetime: str,
        datetime_format: str = "",
        min_datetime: str = "",
        max_datetime: str = "",
    ):
        self._datetime_interpolator = InterpolatedString(datetime)
        self._datetime_format = datetime_format
        self._timezone = dt.timezone.utc
        self._min_datetime_interpolator = InterpolatedString(min_datetime) if min_datetime else None
        self._max_datetime_interpolator = InterpolatedString(max_datetime) if max_datetime else None

    def get_datetime(self, config, **kwargs) -> dt.datetime:
        # We apply a default datetime format here instead of at instantiation, so it can be set by the parent first
        datetime_format = self._datetime_format
        if not datetime_format:
            datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"

        time = dt.datetime.strptime(self._datetime_interpolator.eval(config, **kwargs), datetime_format).replace(tzinfo=self._timezone)

        if self._min_datetime_interpolator:
            min_time = dt.datetime.strptime(self._min_datetime_interpolator.eval(config, **kwargs), datetime_format).replace(
                tzinfo=self._timezone
            )
            time = max(time, min_time)
        if self._max_datetime_interpolator:
            max_time = dt.datetime.strptime(self._max_datetime_interpolator.eval(config, **kwargs), datetime_format).replace(
                tzinfo=self._timezone
            )
            time = min(time, max_time)
        return time

    @property
    def datetime_format(self):
        return self._datetime_format

    @datetime_format.setter
    def datetime_format(self, value):
        self._datetime_format = value
