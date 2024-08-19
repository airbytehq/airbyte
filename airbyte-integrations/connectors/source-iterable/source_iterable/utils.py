#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dateutil.parser
import pendulum


def dateutil_parse(text):
    """
    The custom function `dateutil_parse` replace `pendulum.parse(text, strict=False)` to avoid memory leak.
    More details https://github.com/airbytehq/airbyte/pull/19913
    """
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
