#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import ResponseStatus

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, first_handler_behavior, second_handler_behavior, expected_behavior",
    [
        (
            "test_chain_retrier_ok_ok",
            response_status.SUCCESS,
            response_status.SUCCESS,
            response_status.SUCCESS,
        ),
        (
            "test_chain_retrier_ignore_fail",
            response_status.IGNORE,
            response_status.FAIL,
            response_status.IGNORE,
        ),
        (
            "test_chain_retrier_fail_ignore",
            response_status.FAIL,
            response_status.IGNORE,
            response_status.IGNORE,
        ),
        (
            "test_chain_retrier_ignore_retry",
            response_status.IGNORE,
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            response_status.IGNORE,
        ),
        (
            "test_chain_retrier_retry_ignore",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            response_status.IGNORE,
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_retry_fail",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            response_status.FAIL,
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_fail_retry",
            response_status.FAIL,
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_ignore_ok",
            response_status.IGNORE,
            response_status.SUCCESS,
            response_status.IGNORE,
        ),
        (
            "test_chain_retrier_ok_ignore",
            response_status.SUCCESS,
            response_status.IGNORE,
            response_status.SUCCESS,
        ),
        (
            "test_chain_retrier_ok_retry",
            response_status.SUCCESS,
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            response_status.SUCCESS,
        ),
        (
            "test_chain_retrier_retry_ok",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            response_status.SUCCESS,
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_return_first_retry",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.retry(2 * SOME_BACKOFF_TIME),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
    ],
)
def test_composite_error_handler(test_name, first_handler_behavior, second_handler_behavior, expected_behavior):
    first_error_handler = MagicMock()
    first_error_handler.interpret_response.return_value = first_handler_behavior
    second_error_handler = MagicMock()
    second_error_handler.interpret_response.return_value = second_handler_behavior
    second_error_handler.interpret_response.return_value = second_handler_behavior
    retriers = [first_error_handler, second_error_handler]
    retrier = CompositeErrorHandler(error_handlers=retriers, options={})
    response_mock = MagicMock()
    response_mock.ok = first_handler_behavior == response_status.SUCCESS or second_handler_behavior == response_status.SUCCESS
    assert retrier.interpret_response(response_mock) == expected_behavior


def test_composite_error_handler_no_handlers():
    try:
        CompositeErrorHandler(error_handlers=[], options={})
        assert False
    except ValueError:
        pass
