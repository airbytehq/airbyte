#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import datetime
import unittest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator


class MyTestCase(unittest.TestCase):
    def test_something(self):
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


if __name__ == "__main__":
    unittest.main()
