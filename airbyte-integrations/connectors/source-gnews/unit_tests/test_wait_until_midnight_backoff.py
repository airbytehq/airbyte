#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from source_gnews import WaitUntilMidnightBackoffStrategy

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@pytest.mark.parametrize(
    "test_name, now_utc, expected_backoff_time",
    [
        ("test_under_normal_conditions", "2021-06-10 15:00:30", 32370.0),
        ("test_last_day_of_year", "2021-12-31 23:50:30", 570.0),
        ("test_just_before_midnight", "2021-06-10 23:59:59", 1.0),
        ("test_just_after_midnight", "2021-06-10 00:00:01", 86399.0),
        ("test_just_during_midnight", "2021-06-10 00:00:00", 86400.0),
    ],
)
@patch("source_gnews.wait_until_midnight_backoff_strategy.datetime")
def test_wait_until_midnight(test_datetime, test_name, now_utc, expected_backoff_time):
    test_datetime.utcnow = Mock(return_value=datetime.strptime(now_utc, DATE_FORMAT))
    response_mock = Mock()
    backoff_stratery = WaitUntilMidnightBackoffStrategy(options={}, config={})
    backoff = backoff_stratery.backoff(response_mock, 1)
    assert backoff == expected_backoff_time
