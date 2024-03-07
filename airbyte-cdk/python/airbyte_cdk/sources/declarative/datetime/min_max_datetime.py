#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime as dt
from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


@dataclass
class MinMaxDatetime:
    """
    Compares the provided date against optional minimum or maximum times. If date is earlier than
    min_date, then min_date is returned. If date is greater than max_date, then max_date is returned.
    If neither, the input date is returned.

    The timestamp format accepts the same format codes as datetime.strfptime, which are
    all the format codes required by the 1989 C standard.
    Full list of accepted format codes: https://man7.org/linux/man-pages/man3/strftime.3.html

    Attributes:
        datetime (Union[InterpolatedString, str]): InterpolatedString or string representing the datetime in the format specified by `datetime_format`
        datetime_format (str): Format of the datetime passed as argument
        min_datetime (Union[InterpolatedString, str]): Represents the minimum allowed datetime value.
        max_datetime (Union[InterpolatedString, str]): Represents the maximum allowed datetime value.
    """

    datetime: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]]
    # datetime_format is a unique case where we inherit it from the parent if it is not specified before using the default value
    # which is why we need dedicated getter/setter methods and private dataclass field
    datetime_format: str = ""
    _datetime_format: str = field(init=False, repr=False, default="")
    min_datetime: Union[InterpolatedString, str] = ""
    max_datetime: Union[InterpolatedString, str] = ""

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.datetime = InterpolatedString.create(self.datetime, parameters=parameters or {})
        self._parser = DatetimeParser()
        self.min_datetime = InterpolatedString.create(self.min_datetime, parameters=parameters) if self.min_datetime else None  # type: ignore
        self.max_datetime = InterpolatedString.create(self.max_datetime, parameters=parameters) if self.max_datetime else None  # type: ignore

    def get_datetime(self, config: Mapping[str, Any], **additional_parameters: Mapping[str, Any]) -> dt.datetime:
        """
        Evaluates and returns the datetime
        :param config: The user-provided configuration as specified by the source's spec
        :param additional_parameters: Additional arguments to be passed to the strings for interpolation
        :return: The evaluated datetime
        """
        # We apply a default datetime format here instead of at instantiation, so it can be set by the parent first
        datetime_format = self._datetime_format
        if not datetime_format:
            datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"

        time = self._parser.parse(str(self.datetime.eval(config, **additional_parameters)), datetime_format)  # type: ignore # datetime is always cast to an interpolated string

        if self.min_datetime:
            min_time = str(self.min_datetime.eval(config, **additional_parameters))  # type: ignore # min_datetime is always cast to an interpolated string
            if min_time:
                min_datetime = self._parser.parse(min_time, datetime_format)  # type: ignore # min_datetime is always cast to an interpolated string
                time = max(time, min_datetime)
        if self.max_datetime:
            max_time = str(self.max_datetime.eval(config, **additional_parameters))  # type: ignore # max_datetime is always cast to an interpolated string
            if max_time:
                max_datetime = self._parser.parse(max_time, datetime_format)
                time = min(time, max_datetime)
        return time

    @property  # type: ignore # properties don't play well with dataclasses...
    def datetime_format(self) -> str:
        """The format of the string representing the datetime"""
        return self._datetime_format

    @datetime_format.setter
    def datetime_format(self, value: str) -> None:
        """Setter for the datetime format"""
        # Covers the case where datetime_format is not provided in the constructor, which causes the property object
        # to be set which we need to avoid doing
        if not isinstance(value, property):
            self._datetime_format = value

    @classmethod
    def create(
        cls,
        interpolated_string_or_min_max_datetime: Union[InterpolatedString, str, "MinMaxDatetime"],
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> "MinMaxDatetime":
        if parameters is None:
            parameters = {}
        if isinstance(interpolated_string_or_min_max_datetime, InterpolatedString) or isinstance(
            interpolated_string_or_min_max_datetime, str
        ):
            return MinMaxDatetime(datetime=interpolated_string_or_min_max_datetime, parameters=parameters)
        else:
            return interpolated_string_or_min_max_datetime
