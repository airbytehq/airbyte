#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import builtins
import datetime
import numbers
from typing import Union

from dateutil import parser
from dateutil import tz as dateutil_tz

"""
This file contains macros that can be evaluated by a `JinjaInterpolation` object
"""


def now_local() -> datetime.datetime:
    """
    Current local date and time.

    Usage:
    `"{{ now_local() }}"
    """
    return datetime.datetime.now()


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
        return int(parser.parse(dt).replace(tzinfo=datetime.timezone.utc).timestamp())


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


def day_delta(num_days: int, from_date: Union[str, datetime.datetime] = None) -> str:
    """
    Returns datetime of now() + num_days if not from_date is provided, otherwise returns datetime of from_date + num_days

    Usage:
    `"{{ day_delta(25) }}"`
    `"{{ day_delta(25, '2021-01-01') }}"`

    :param num_days: number of days to add to current date time
    :param from_date: date time to add num_days to
    :return: datetime formatted as RFC3339
    """
    if from_date is None:
        from_date = datetime.datetime.now(datetime.timezone.utc)
    elif isinstance(from_date, str):
        from_date = parser.parse(from_date)
    return (from_date + datetime.timedelta(days=num_days)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def format_datetime(dt: Union[str, datetime.datetime], format: str):
    """
    Converts datetime to another format

    Usage:
    `"{{ format_datetime(config.start_date, '%Y-%m-%d') }}"`
    """
    if isinstance(dt, datetime.datetime):
        return dt.strftime(format)
    return parser.parse(dt).strftime(format)


def as_timezone(dt: Union[str, datetime.datetime], timezone: str):
    """
    Converts datetime to another timezone

    Usage:
    `"{{ as_timezone(config.start_date, 'America/New_York') }}"`
    """
    if isinstance(dt, datetime.datetime):
        return dt.astimezone(dateutil_tz.gettz(timezone))
    return parser.parse(dt).astimezone(dateutil_tz.gettz(timezone))


_macros_list = [now_local, now_utc, today_utc, timestamp, max, day_delta, format_datetime, as_timezone]
macros = {f.__name__: f for f in _macros_list}
