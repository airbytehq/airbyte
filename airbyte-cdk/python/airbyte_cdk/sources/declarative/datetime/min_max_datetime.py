#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime as dt
from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class MinMaxDatetime(JsonSchemaMixin):
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
    options: InitVar[Mapping[str, Any]]
    # datetime_format is a unique case where we inherit it from the parent if it is not specified before using the default value
    # which is why we need dedicated getter/setter methods and private dataclass field
    datetime_format: str = ""
    _datetime_format: str = field(init=False, repr=False, default="")
    min_datetime: Union[InterpolatedString, str] = ""
    max_datetime: Union[InterpolatedString, str] = ""

    def __post_init__(self, options: Mapping[str, Any]):
        self.datetime = InterpolatedString.create(self.datetime, options=options or {})
        self.timezone = dt.timezone.utc
        self._parser = DatetimeParser()
        self.min_datetime = InterpolatedString.create(self.min_datetime, options=options) if self.min_datetime else None
        self.max_datetime = InterpolatedString.create(self.max_datetime, options=options) if self.max_datetime else None

        self._timezone = dt.timezone.utc

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

        time = self._parser.parse(str(self.datetime.eval(config, **additional_options)), datetime_format, self.timezone)

        if self.min_datetime:
            min_time = self._parser.parse(str(self.min_datetime.eval(config, **additional_options)), datetime_format, self.timezone)
            time = max(time, min_time)
        if self.max_datetime:
            max_time = self._parser.parse(str(self.max_datetime.eval(config, **additional_options)), datetime_format, self.timezone)
            time = min(time, max_time)
        return time

    @property
    def datetime_format(self) -> str:
        """The format of the string representing the datetime"""
        return self._datetime_format

    @datetime_format.setter
    def datetime_format(self, value: str):
        """Setter for the datetime format"""
        # Covers the case where datetime_format is not provided in the constructor, which causes the property object
        # to be set which we need to avoid doing
        if not isinstance(value, property):
            self._datetime_format = value
