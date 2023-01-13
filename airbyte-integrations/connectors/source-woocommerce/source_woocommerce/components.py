#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.sources.declarative.stream_slicers import DatetimeStreamSlicer


class DatetimeStreamSlicerWoocommerce(DatetimeStreamSlicer):

    # TODO: remove whole method after solving https://github.com/airbytehq/airbyte/issues/20322
    def _partition_daterange(self, start, end, step: datetime.timedelta):
        start_field = self.stream_slice_field_start.eval(self.config)
        end_field = self.stream_slice_field_end.eval(self.config)
        dates = []
        while start <= end:
            # interval hardcoded to 1 second, as we have datetime_format: "%Y-%m-%dT%H:%M:%S"
            end_date = self._get_date(start + step - datetime.timedelta(seconds=1), end, min)
            dates.append({start_field: self._format_datetime(start), end_field: self._format_datetime(end_date)})
            start += step
        return dates
