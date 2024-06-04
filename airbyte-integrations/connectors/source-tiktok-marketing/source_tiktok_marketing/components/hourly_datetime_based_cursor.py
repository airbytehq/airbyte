# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime
from typing import List, Union

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.types import StreamSlice
from isodate import Duration


class HourlyDatetimeBasedCursor(DatetimeBasedCursor):
    """
    We need to overwrite _partition_daterange to replace hour=0, minute=0, second=0, microsecond=0 in start value in slices
    because it is used as request params.
    TikTok Marketing API doesn't allow date range more than one day.
    In case when start date 2024-01-01 10:00:00 with step P1D slices look like {'start_time': '2024-01-01', 'end_time': '2024-01-02'},
    so API returns the following error:
    'code': 40002, 'message': 'max time span is 1 day when use stat_time_hour'.
    To avoid such cases we replace start hours/minutes/seconds to 0 to have correct request params.
    DatetimeBasedCursor uses _partition_daterange to create stream_slices.
    """

    def _partition_daterange(
        self, start: datetime.datetime, end: datetime.datetime, step: Union[datetime.timedelta, Duration]
    ) -> List[StreamSlice]:
        start = start.replace(hour=0, minute=0, second=0)
        return super()._partition_daterange(start, end, step)
