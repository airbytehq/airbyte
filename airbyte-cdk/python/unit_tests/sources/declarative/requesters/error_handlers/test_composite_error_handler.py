#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import ResponseStatus

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, first_handler_behavior, second_handler_behavior, expected_behavior",
    [
        (
            "test_chain_retrier_ok_ok",
            ResponseStatus.success(),
            ResponseStatus.success(),
            ResponseStatus.success(),
        ),
        (
            "test_chain_retrier_ignore_fail",
            ResponseStatus.ignore(),
            ResponseStatus.fail(),
            ResponseStatus.ignore(),
        ),
        (
            "test_chain_retrier_fail_ignore",
            ResponseStatus.fail(),
            ResponseStatus.ignore(),
            ResponseStatus.ignore(),
        ),
        (
            "test_chain_retrier_ignore_retry",
            ResponseStatus.ignore(),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.ignore(),
        ),
        (
            "test_chain_retrier_retry_ignore",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.ignore(),
            ResponseStatus.ignore(),
        ),
        (
            "test_chain_retrier_retry_fail",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.fail(),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_fail_retry",
            ResponseStatus.fail(),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_ignore_ok",
            ResponseStatus.ignore(),
            ResponseStatus.success(),
            ResponseStatus.success(),
        ),
        (
            "test_chain_retrier_ok_ignore",
            ResponseStatus.success(),
            ResponseStatus.ignore(),
            ResponseStatus.success(),
        ),
        (
            "test_chain_retrier_ok_retry",
            ResponseStatus.success(),
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.success(),
        ),
        (
            "test_chain_retrier_retry_ok",
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            ResponseStatus.success(),
            ResponseStatus.success(),
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
    first_error_handler.should_retry.return_value = first_handler_behavior
    second_error_handler = MagicMock()
    second_error_handler.should_retry.return_value = second_handler_behavior
    second_error_handler.should_retry.return_value = second_handler_behavior
    retriers = [first_error_handler, second_error_handler]
    retrier = CompositeErrorHandler(retriers)
    response_mock = MagicMock()
    response_mock.ok = first_handler_behavior == ResponseStatus.success() or second_handler_behavior == ResponseStatus.success()
    assert retrier.should_retry(response_mock) == expected_behavior
