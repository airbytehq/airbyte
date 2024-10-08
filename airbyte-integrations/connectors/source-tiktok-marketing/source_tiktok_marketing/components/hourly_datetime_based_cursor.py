# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Iterable

from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.types import StreamSlice


class HourlyDatetimeBasedCursor(DatetimeBasedCursor):
    """
    We need to overwrite stream_slices to replace hour=0, minute=0, second=0, microsecond=0 in start value in slices
    because it is used as request params.
    TikTok Marketing API doesn't allow date range more than one day.
    In case when start date 2024-01-01 10:00:00 with step P1D slices look like {'start_time': '2024-01-01', 'end_time': '2024-01-02'},
    so API returns the following error:
    'code': 40002, 'message': 'max time span is 1 day when use stat_time_hour'.
    To avoid such cases we replace start hours/minutes/seconds to 0 to have correct request params.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Partition the daterange into slices of size = step.

        The start of the window is the minimum datetime between start_datetime - lookback_window and the stream_state's datetime
        The end of the window is the minimum datetime between the start of the window and end_datetime.

        :return:
        """
        end_datetime = self.select_best_end_datetime()
        start_datetime = self._calculate_earliest_possible_value(self.select_best_end_datetime()).replace(hour=0, minute=0, second=0)
        return self._partition_daterange(start_datetime, end_datetime, self._step)
