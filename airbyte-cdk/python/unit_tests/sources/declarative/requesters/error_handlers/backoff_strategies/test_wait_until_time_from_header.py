#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_until_time_from_header_backoff_strategy import (
    WaitUntilTimeFromHeaderBackoffStrategy,
)

SOME_BACKOFF_TIME = 60
REGEX = "[-+]?\\d+"


@pytest.mark.parametrize(
    "test_name, header, wait_until, min_wait, regex, expected_backoff_time",
    [
        ("test_wait_until_time_from_header", "wait_until", 1600000060.0, None, None, 60),
        ("test_wait_until_time_from_header_parameters", "{{parameters['wait_until']}}", 1600000060.0, None, None, 60),
        ("test_wait_until_time_from_header_config", "{{config['wait_until']}}", 1600000060.0, None, None, 60),
        ("test_wait_until_negative_time", "wait_until", 1500000000.0, None, None, None),
        ("test_wait_until_time_less_than_min", "wait_until", 1600000060.0, 120, None, 120),
        ("test_wait_until_no_header", "absent_header", 1600000000.0, None, None, None),
        ("test_wait_until_time_from_header_not_numeric", "wait_until", "1600000000,1600000000", None, None, None),
        ("test_wait_until_time_from_header_is_numeric", "wait_until", "1600000060", None, None, 60),
        ("test_wait_until_time_from_header_with_regex", "wait_until", "1600000060,60", None, "[-+]?\d+", 60),  # noqa
        ("test_wait_until_time_from_header_with_regex_from_parameters", "wait_until", "1600000060,60", None, "{{parameters['regex']}}", 60),
        # noqa
        ("test_wait_until_time_from_header_with_regex_from_config", "wait_until", "1600000060,60", None, "{{config['regex']}}", 60),  # noqa
        ("test_wait_until_time_from_header_with_regex_no_match", "wait_time", "...", None, "[-+]?\d+", None),  # noqa
        ("test_wait_until_no_header_with_min", "absent_header", "1600000000.0", SOME_BACKOFF_TIME, None, SOME_BACKOFF_TIME),
        (
            "test_wait_until_no_header_with_min_from_parameters",
            "absent_header",
            "1600000000.0",
            "{{parameters['min_wait']}}",
            None,
            SOME_BACKOFF_TIME,
        ),
        (
            "test_wait_until_no_header_with_min_from_config",
            "absent_header",
            "1600000000.0",
            "{{config['min_wait']}}",
            None,
            SOME_BACKOFF_TIME,
        ),
    ],
)
@patch("time.time", return_value=1600000000.0)
def test_wait_untiltime_from_header(time_mock, test_name, header, wait_until, min_wait, regex, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.headers = {"wait_until": wait_until}
    backoff_stratery = WaitUntilTimeFromHeaderBackoffStrategy(
        header=header,
        min_wait=min_wait,
        regex=regex,
        parameters={"wait_until": "wait_until", "regex": REGEX, "min_wait": SOME_BACKOFF_TIME},
        config={"wait_until": "wait_until", "regex": REGEX, "min_wait": SOME_BACKOFF_TIME},
    )
    backoff = backoff_stratery.backoff(response_mock, 1)
    assert backoff == expected_backoff_time
