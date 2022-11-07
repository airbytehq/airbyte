#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, header, header_value, regex, expected_backoff_time",
    [
        ("test_wait_time_from_header", "wait_time", SOME_BACKOFF_TIME, None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_string", "wait_time", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_options", "{{ options['wait_time'] }}", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_config", "{{ config['wait_time'] }}", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_not_a_number", "wait_time", "61,60", None, None),
        ("test_wait_time_from_header_with_regex", "wait_time", "61,60", "([-+]?\d+)", 61),  # noqa
        ("test_wait_time_fœrom_header_with_regex_no_match", "wait_time", "...", "[-+]?\d+", None),  # noqa
        ("test_wait_time_from_header", "absent_header", None, None, None),
    ],
)
def test_wait_time_from_header(test_name, header, header_value, regex, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.headers = {"wait_time": header_value}
    backoff_stratery = WaitTimeFromHeaderBackoffStrategy(
        header=header, regex=regex, options={"wait_time": "wait_time"}, config={"wait_time": "wait_time"}
    )
    backoff = backoff_stratery.backoff(response_mock, 1)
    assert backoff == expected_backoff_time
