#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Iterable, Optional

import pendulum
from pendulum import DateTime, Period


def chunk_date_range(start_date: DateTime, interval=pendulum.duration(days=100), end_date: Optional[DateTime] = None) -> Iterable[Period]:
    """
    Yields a list of the beginning and ending timestamps of each day between the start date and now.
    The return value is a pendulum.period
    """

    end_date = end_date or pendulum.now()
    # Each stream_slice contains the beginning and ending timestamp for a 24 hour period
    chunk_start_date = start_date
    while chunk_start_date < end_date:
        chunk_end_date = min(chunk_start_date + interval, end_date)
        yield pendulum.period(chunk_start_date, chunk_end_date)
        chunk_start_date = chunk_end_date
