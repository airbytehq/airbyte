#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import builtins
import datetime
import numbers
from typing import Union

from dateutil import parser
from isodate import parse_duration

"""
This file contains macros that can be evaluated by a `JinjaInterpolation` object
"""


def now_utc():
    """
    Current local date and time in UTC timezone

    Usage:
    `"{{ now_utc() }}"`
    """
    return datetime.datetime.now(datetime.timezone.utc)


def today_utc():
    """
    Current date in UTC timezone

    Usage:
    `"{{ today_utc() }}"`
    """
    return datetime.datetime.now(datetime.timezone.utc).date()


def timestamp(dt: Union[numbers.Number, str]):
    """
    Converts a number or a string to a timestamp

    If dt is a number, then convert to an int
    If dt is a string, then parse it using dateutil.parser

    Usage:
    `"{{ timestamp(1658505815.223235) }}"

    :param dt: datetime to convert to timestamp
    :return: unix timestamp
    """
    if isinstance(dt, numbers.Number):
        return int(dt)
    else:
        return _str_to_datetime(dt).astimezone(datetime.timezone.utc).timestamp()


def _str_to_datetime(s: str) -> datetime.datetime:
    parsed_date = parser.isoparse(s)
    if not parsed_date.tzinfo:
        # Assume UTC if the input does not contain a timezone
        parsed_date = parsed_date.replace(tzinfo=datetime.timezone.utc)
    return parsed_date.astimezone(datetime.timezone.utc)


def max(*args):
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


def duration(datestring: str) -> datetime.timedelta:
    """
    Converts ISO8601 duration to datetime.timedelta

    Usage:
    `"{{ now_utc() - duration('P1D') }}"`
    """
    return parse_duration(datestring)


def format_datetime(dt: Union[str, datetime.datetime], format: str) -> str:
    """
    Converts datetime to another format

    Usage:
    `"{{ format_datetime(config.start_date, '%Y-%m-%d') }}"`
    """
    if isinstance(dt, datetime.datetime):
        return dt.strftime(format)
    return _str_to_datetime(dt).strftime(format)


_macros_list = [now_utc, today_utc, timestamp, max, day_delta, duration, format_datetime]
macros = {f.__name__: f for f in _macros_list}
