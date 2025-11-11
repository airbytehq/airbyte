#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Union


class DatetimeParser:
    """
    Parses and formats datetime objects according to a specified format.

    This class mainly acts as a wrapper to properly handling timestamp formatting through the "%s" directive.

    %s is part of the list of format codes required by  the 1989 C standard, but it is unreliable because it always return a datetime in the system's timezone.
    Instead of using the directive directly, we can use datetime.fromtimestamp and dt.timestamp()
    """

    _UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    def parse(self, date: Union[str, int], format: str) -> datetime.datetime:
        # "%s" is a valid (but unreliable) directive for formatting, but not for parsing
        # It is defined as
        # The number of seconds since the Epoch, 1970-01-01 00:00:00+0000 (UTC). https://man7.org/linux/man-pages/man3/strptime.3.html
        #
        # The recommended way to parse a date from its timestamp representation is to use datetime.fromtimestamp
        # See https://stackoverflow.com/a/4974930
        if format == "%s":
            return datetime.datetime.fromtimestamp(int(date), tz=datetime.timezone.utc)
        elif format == "%s_as_float":
            return datetime.datetime.fromtimestamp(float(date), tz=datetime.timezone.utc)
        elif format == "%epoch_microseconds":
            return self._UNIX_EPOCH + datetime.timedelta(microseconds=int(date))
        elif format == "%ms":
            return self._UNIX_EPOCH + datetime.timedelta(milliseconds=int(date))
        elif "%_ms" in format:
            format = format.replace("%_ms", "%f")
        parsed_datetime = datetime.datetime.strptime(str(date), format)
        if self._is_naive(parsed_datetime):
            return parsed_datetime.replace(tzinfo=datetime.timezone.utc)
        return parsed_datetime

    def format(self, dt: datetime.datetime, format: str) -> str:
        # strftime("%s") is unreliable because it ignores the time zone information and assumes the time zone of the system it's running on
        # It's safer to use the timestamp() method than the %s directive
        # See https://stackoverflow.com/a/4974930
        if format == "%s":
            return str(int(dt.timestamp()))
        if format == "%s_as_float":
            return str(float(dt.timestamp()))
        if format == "%epoch_microseconds":
            return str(int(dt.timestamp() * 1_000_000))
        if format == "%ms":
            # timstamp() returns a float representing the number of seconds since the unix epoch
            return str(int(dt.timestamp() * 1000))
        if "%_ms" in format:
            _format = format.replace("%_ms", "%f")
            milliseconds = int(dt.microsecond / 1000)
            formatted_dt = dt.strftime(_format).replace(dt.strftime("%f"), "%03d" % milliseconds)
            return formatted_dt
        else:
            return dt.strftime(format)

    def _is_naive(self, dt: datetime.datetime) -> bool:
        return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None
