#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from source_intercom.utils import IntercomRateLimiter as limiter

TEST_DATA_FIELD = "some_data_field"
TEST_RATE_LIMIT_HEADER = "X-RateLimit-Limit"
TEST_RATE_LIMIT_REMAIN_HEADER = "X-RateLimit-Remaining"
TEST_THRESHOLD = 0.1


@pytest.mark.parametrize(
    "headers, expected",
    [
        ({"no_rate_limit_header": "no_values"}, limiter.on_unknown_load),
        ({"X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "90"}, limiter.on_low_load),
        ({"X-RateLimit-Limit": "167", "X-RateLimit-Remaining": "80"}, limiter.on_mid_load),
        ({"X-RateLimit-Limit": "200", "X-RateLimit-Remaining": "20"}, limiter.on_high_load),
    ],
    ids=[
        "On UNKNOWN load",
        "On Low Load",
        "On Mid Load",
        "On High Load",
    ],
)
def test_with_unknown_load(requests_mock, headers, expected):
    """
    Test simulates the case with unknown load because of missing rate limit header.
    In this case we should wait 1.0 sec sleep before next API call.
    """
    requests_mock.get("https://api.intercom.io/", headers=headers)
    test_response = requests.get("https://api.intercom.io/")
    actual_sleep_time = limiter.get_wait_time(
        test_response,
        threshold=TEST_THRESHOLD,
        rate_limit_header=TEST_RATE_LIMIT_HEADER,
        rate_limit_remain_header=TEST_RATE_LIMIT_REMAIN_HEADER,
    )
    assert expected == actual_sleep_time
