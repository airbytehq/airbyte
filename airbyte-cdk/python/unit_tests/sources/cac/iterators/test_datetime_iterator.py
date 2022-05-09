#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
import unittest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator


class MyTestCase(unittest.TestCase):
    def test_date_1_day_chunks(self):
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)
        step = datetime.timedelta(days=1)
        timezone = datetime.timezone.utc
        vars = {}
        config = {}
        iterator = DatetimeIterator(start_date, end_date, step, timezone, vars, config)
        stream_state = None
        stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)
        self.assertEqual(len(stream_slices), 366)

    def test_date_1_month_chunks(self):
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)
        step = datetime.timedelta(days=30)
        timezone = datetime.timezone.utc
        vars = {}
        config = {}
        iterator = DatetimeIterator(start_date, end_date, step, timezone, vars, config)
        stream_state = None
        stream_slices = iterator.stream_slices(SyncMode.incremental, stream_state)
        self.assertEqual(len(stream_slices), 13)

    def test_end_date_past_now(self):
        # FIXME: add a test where end_date is past datetime.now()
        pass

    def test_start_date_after_end_date(self):
        # FIXME: add a test where start_date is past end_date
        pass


if __name__ == "__main__":
    unittest.main()
