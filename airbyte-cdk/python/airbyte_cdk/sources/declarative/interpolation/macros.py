#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import builtins
import datetime
import typing
from typing import Optional, Union

import isodate
import pytz
from dateutil import parser
from isodate import parse_duration

"""
This file contains macros that can be evaluated by a `JinjaInterpolation` object
"""


def now_utc() -> datetime.datetime:
    """
    Current local date and time in UTC timezone

    Usage:
    `"{{ now_utc() }}"`
    """
    return datetime.datetime.now(datetime.timezone.utc)


def today_utc() -> datetime.date:
    """
    Current date in UTC timezone

    Usage:
    `"{{ today_utc() }}"`
    """
    return datetime.datetime.now(datetime.timezone.utc).date()


def timestamp(dt: Union[float, str]) -> Union[int, float]:
    """
    Converts a number or a string to a timestamp

    If dt is a number, then convert to an int
    If dt is a string, then parse it using dateutil.parser

    Usage:
    `"{{ timestamp(1658505815.223235) }}"

    :param dt: datetime to convert to timestamp
    :return: unix timestamp
    """
    if isinstance(dt, (int, float)):
        return int(dt)
    else:
        return _str_to_datetime(dt).astimezone(pytz.utc).timestamp()


def _str_to_datetime(s: str) -> datetime.datetime:
    parsed_date = parser.isoparse(s)
    if not parsed_date.tzinfo:
        # Assume UTC if the input does not contain a timezone
        parsed_date = parsed_date.replace(tzinfo=pytz.utc)
    return parsed_date.astimezone(pytz.utc)


def max(*args: typing.Any) -> typing.Any:
    """
    Returns biggest object of an iterable, or two or more arguments.

    max(iterable, *[, default=obj, key=func]) -> value
    max(arg1, arg2, *args, *[, key=func]) -> value

    Usage:
    `"{{ max(2,3) }}"

    With a single iterable argument, return its biggest item. The
    default keyword-only argument specifies an object to return if
    the provided iterable is empty.
    With two or more arguments, return the largest argument.
    :param args: args to compare
    :return: largest argument
    """
    return builtins.max(*args)


def day_delta(num_days: int, format: str = "%Y-%m-%dT%H:%M:%S.%f%z") -> str:
    """
    Returns datetime of now() + num_days

    Usage:
    `"{{ day_delta(25) }}"`

    :param num_days: number of days to add to current date time
    :return: datetime formatted as RFC3339
    """
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=num_days)).strftime(format)


def duration(datestring: str) -> Union[datetime.timedelta, isodate.Duration]:
    """
    Converts ISO8601 duration to datetime.timedelta

    Usage:
    `"{{ now_utc() - duration('P1D') }}"`
    """
    return parse_duration(datestring)  # type: ignore # mypy thinks this returns Any for some reason


def format_datetime(dt: Union[str, datetime.datetime], format: str, input_format: Optional[str] = None) -> str:
    """
    Converts datetime to another format

    Usage:
    `"{{ format_datetime(config.start_date, '%Y-%m-%d') }}"`

    CPython Datetime package has known bug with `stfrtime` method: '%s' formatting uses locale timezone
    https://github.com/python/cpython/issues/77169
    https://github.com/python/cpython/issues/56959
    """
    if isinstance(dt, datetime.datetime):
        return dt.strftime(format)
    dt_datetime = datetime.datetime.strptime(dt, input_format) if input_format else _str_to_datetime(dt)
    if format == "%s":
        return str(int(dt_datetime.timestamp()))
    return dt_datetime.strftime(format)


_macros_list = [now_utc, today_utc, timestamp, max, day_delta, duration, format_datetime]
macros = {f.__name__: f for f in _macros_list}
