#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import List, Union
from dataclasses import dataclass
from isodate import Duration, parse_duration
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class SnapchatMarketingDatetimeBasedCursor(DatetimeBasedCursor):
    """
    SnapchatMarketingDatetimeBasedCursor is a variant of DatetimeBasedCursor that strictly compares start and end dates.
    It ensures that the start date is always less than the end date to prevent errors.
    """

    def _partition_daterange(
        self, start: datetime, end: datetime, step: Union[timedelta, Duration]
    ) -> List[StreamSlice]:
        start_field = self._partition_field_start.eval(self.config)
        end_field = self._partition_field_end.eval(self.config)
        dates = []

        while start < end:
            next_start = self._evaluate_next_start_date_safely(start, step)
            end_date = self._get_date(next_start - self._cursor_granularity, end, min)

            dates.append(
                StreamSlice(
                    partition={},
                    cursor_slice={
                        start_field: self._format_datetime(start),
                        end_field: self._format_datetime(end_date)
                    }
                )
            )

            start = next_start

        return dates
