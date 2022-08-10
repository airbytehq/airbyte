#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

    def parse(self, date: Union[str, int], format: str, timezone):
        # "%s" is a valid (but unreliable) directive for formatting, but not for parsing
        # It is defined as
        # The number of seconds since the Epoch, 1970-01-01 00:00:00+0000 (UTC). https://man7.org/linux/man-pages/man3/strptime.3.html
        #
        # The recommended way to parse a date from its timestamp representation is to use datetime.fromtimestamp
        # See https://stackoverflow.com/a/4974930
        if format == "%s":
            return datetime.datetime.fromtimestamp(int(date), tz=timezone)
        else:
            return datetime.datetime.strptime(str(date), format).replace(tzinfo=timezone)

    def format(self, dt: datetime.datetime, format: str) -> str:
        # strftime("%s") is unreliable because it ignores the time zone information and assumes the time zone of the system it's running on
        # It's safer to use the timestamp() method than the %s directive
        # See https://stackoverflow.com/a/4974930
        if format == "%s":
            return str(int(dt.timestamp()))
        else:
            return dt.strftime(format)
