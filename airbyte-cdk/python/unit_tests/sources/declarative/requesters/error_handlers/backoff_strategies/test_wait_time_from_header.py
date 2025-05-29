#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)
from requests import Response

SOME_BACKOFF_TIME = 60
_A_RETRY_HEADER = "retry-header"
_A_MAX_TIME = 100


@pytest.mark.parametrize(
    "test_name, header, header_value, regex, expected_backoff_time",
    [
        ("test_wait_time_from_header", "wait_time", SOME_BACKOFF_TIME, None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_string", "wait_time", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_parameters", "{{ parameters['wait_time'] }}", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_config", "{{ config['wait_time'] }}", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_not_a_number", "wait_time", "61,60", None, None),
        ("test_wait_time_from_header_with_regex", "wait_time", "61,60", "([-+]?\d+)", 61),  # noqa
        ("test_wait_time_fœrom_header_with_regex_no_match", "wait_time", "...", "[-+]?\d+", None),  # noqa
        ("test_wait_time_from_header", "absent_header", None, None, None),
    ],
)
def test_wait_time_from_header(test_name, header, header_value, regex, expected_backoff_time):
    response_mock = MagicMock(spec=Response)
    response_mock.headers = {"wait_time": header_value}
    backoff_strategy = WaitTimeFromHeaderBackoffStrategy(
        header=header, regex=regex, parameters={"wait_time": "wait_time"}, config={"wait_time": "wait_time"}
    )
    backoff = backoff_strategy.backoff_time(response_mock, 1)
    assert backoff == expected_backoff_time


def test_given_retry_after_smaller_than_max_time_then_raise_transient_error():
    response_mock = MagicMock(spec=Response)
    retry_after = _A_MAX_TIME - 1
    response_mock.headers = {_A_RETRY_HEADER: str(retry_after)}
    backoff_strategy = WaitTimeFromHeaderBackoffStrategy(
        header=_A_RETRY_HEADER, max_waiting_time_in_seconds=_A_MAX_TIME, parameters={}, config={}
    )

    assert backoff_strategy.backoff_time(response_mock, 1) == retry_after


def test_given_retry_after_greater_than_max_time_then_raise_transient_error():
    response_mock = MagicMock(spec=Response)
    response_mock.headers = {_A_RETRY_HEADER: str(_A_MAX_TIME + 1)}
    backoff_strategy = WaitTimeFromHeaderBackoffStrategy(
        header=_A_RETRY_HEADER, max_waiting_time_in_seconds=_A_MAX_TIME, parameters={}, config={}
    )

    with pytest.raises(AirbyteTracedException) as exception:
        backoff_strategy.backoff_time(response_mock, 1)
    assert exception.value.failure_type == FailureType.transient_error
