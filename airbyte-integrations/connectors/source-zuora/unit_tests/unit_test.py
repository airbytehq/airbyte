#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from datetime import datetime
from source_zuora.source import ZuoraObjectsBase
import pendulum

class TestZuoraObjectsBase(unittest.TestCase):
    def test_to_datetime_str(self):
        original_str = '2021-07-15 07:45:55.000-07:00'
        expected_str = '2021-07-15 07:45:55.000 -07:00'
        date = pendulum.parse(original_str)
        generated_str = ZuoraObjectsBase.to_datetime_str(date)
        self.assertEqual(expected_str, generated_str)

    def test_to_datetime_str_without_tz(self):
        original_str = '2021-07-15 07:45:55.000'
        expected_str = '2021-07-15 07:45:55.000 +00:00'
        date = pendulum.parse(original_str)
        generated_str = ZuoraObjectsBase.to_datetime_str(date)
        self.assertEqual(expected_str, generated_str)
