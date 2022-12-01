#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import dateutil.parser
import pendulum


def dateutil_parse(text):
    dt = dateutil.parser.parse(text)
    return pendulum.datetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        tz=dt.tzinfo or pendulum.tz.UTC,
    )
