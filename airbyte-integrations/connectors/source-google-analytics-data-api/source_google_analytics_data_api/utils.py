#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import calendar
import datetime


def datetime_to_secs(dt: datetime.datetime) -> int:
    return calendar.timegm(dt.utctimetuple())


def string_to_date(d: str, f: str = "%Y-%m-%d") -> datetime.date:
    return datetime.datetime.strptime(d, f).date()


def date_to_string(d: datetime.date, f: str = "%Y-%m-%d") -> str:
    return d.strftime(f)
