#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime as dt
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class MinMaxDatetime:
    """
    Compares the provided date against optional minimum or maximum times. If date is earlier than
    min_date, then min_date is returned. If date is greater than max_date, then max_date is returned.
    If neither, the input date is returned.
    """

    def __init__(
        self,
        datetime: Union[InterpolatedString, str],
        datetime_format: str = "",
        min_datetime: Union[InterpolatedString, str] = "",
        max_datetime: Union[InterpolatedString, str] = "",
        **options: Optional[Mapping[str, Any]],
    ):
        """
        :param datetime: InterpolatedString or string representing the datetime in the format specified by `datetime_format`
        :param datetime_format: Format of the datetime passed as argument
        :param min_datetime: InterpolatedString or string representing the min datetime
        :param max_datetime: InterpolatedString or string representing the max datetime
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._datetime_interpolator = InterpolatedString.create(datetime, options=options)
        self._datetime_format = datetime_format
        self._timezone = dt.timezone.utc
        self._min_datetime_interpolator = InterpolatedString.create(min_datetime, options=options) if min_datetime else None
        self._max_datetime_interpolator = InterpolatedString.create(max_datetime, options=options) if max_datetime else None

    def get_datetime(self, config, **additional_options) -> dt.datetime:
        """
        Evaluates and returns the datetime
        :param config: The user-provided configuration as specified by the source's spec
        :param additional_options: Additional arguments to be passed to the strings for interpolation
        :return: The evaluated datetime
        """
        # We apply a default datetime format here instead of at instantiation, so it can be set by the parent first
        datetime_format = self._datetime_format
        if not datetime_format:
            datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"

        time = dt.datetime.strptime(self._datetime_interpolator.eval(config, **additional_options), datetime_format).replace(
            tzinfo=self._timezone
        )

        if self._min_datetime_interpolator:
            min_time = dt.datetime.strptime(self._min_datetime_interpolator.eval(config, **additional_options), datetime_format).replace(
                tzinfo=self._timezone
            )
            time = max(time, min_time)
        if self._max_datetime_interpolator:
            max_time = dt.datetime.strptime(self._max_datetime_interpolator.eval(config, **additional_options), datetime_format).replace(
                tzinfo=self._timezone
            )
            time = min(time, max_time)
        return time

    @property
    def datetime_format(self) -> str:
        """The format of the string representing the datetime"""
        return self._datetime_format

    @datetime_format.setter
    def datetime_format(self, value: str):
        """Setter for the datetime format"""
        self._datetime_format = value
