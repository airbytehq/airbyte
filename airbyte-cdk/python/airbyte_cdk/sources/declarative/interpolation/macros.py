#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import builtins
import datetime
import numbers
from typing import Union

from dateutil import parser


def now_local() -> datetime.datetime:
    """
    :return: current local date and time.
    """
    return datetime.datetime.now()


def now_utc():
    """

    :return: current local date and time in utc
    """
    return datetime.datetime.now(datetime.timezone.utc)


def today_utc():
    """

    :return: current date in utc
    """
    return datetime.datetime.now(datetime.timezone.utc).date()


def timestamp(dt: Union[numbers.Number, str]):
    """
    Converts a number or a string to a timestamp
    If dt is a number, then convert to an int
    If dt is a string, then parse it using dateutil.parser
    :param dt: datetime to convert to timestamp
    :return: unix timestamp
    """
    if isinstance(dt, numbers.Number):
        return int(dt)
    else:
        return int(parser.parse(dt).replace(tzinfo=datetime.timezone.utc).timestamp())


def max(*args):
    """
        max(iterable, *[, default=obj, key=func]) -> value
        max(arg1, arg2, *args, *[, key=func]) -> value

        With a single iterable argument, return its biggest item. The
        default keyword-only argument specifies an object to return if
        the provided iterable is empty.
        With two or more arguments, return the largest argument.
    :param args:
    :return: largest argument
    """
    return builtins.max(*args)


def day_delta(num_days: int) -> str:
    """
    Returns datetime of now() + num_days
    :param num_days: number of days to add to current date time
    :return: datetime formatted as RFC3339
    """
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=num_days)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


_macros_list = [now_local, now_utc, today_utc, timestamp, max, day_delta]
macros = {f.__name__: f for f in _macros_list}
