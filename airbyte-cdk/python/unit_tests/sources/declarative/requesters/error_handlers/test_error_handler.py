#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_until_time_from_header_backoff_strategy import (
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import (
    DefaultErrorHandler,
    HttpResponseFilter,
    ResponseStatus,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ResponseAction

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, http_code, retry_response_filter, ignore_response_filter, response_headers, should_retry, backoff_strategy",
    [
        ("test_bad_gateway", HTTPStatus.BAD_GATEWAY, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_bad_gateway_constant_retry",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            [ConstantBackoffStrategy(SOME_BACKOFF_TIME)],
        ),
        ("test_exponential_backoff", HTTPStatus.BAD_GATEWAY, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_bad_gateway_exponential_backoff_explicit_parameter",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            ResponseStatus.retry(10),
            [DefaultErrorHandler.DEFAULT_BACKOFF_STRATEGY()],
        ),
        ("test_chain_backoff_strategy", HTTPStatus.BAD_GATEWAY, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_bad_gateway_chain_backoff",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            ResponseStatus.retry(10),
            [DefaultErrorHandler.DEFAULT_BACKOFF_STRATEGY(), ConstantBackoffStrategy(SOME_BACKOFF_TIME)],
        ),
        ("test_200", HTTPStatus.OK, None, None, {}, ResponseStatus.success(), None),
        ("test_3XX", HTTPStatus.PERMANENT_REDIRECT, None, None, {}, ResponseStatus.success(), None),
        ("test_403", HTTPStatus.FORBIDDEN, None, None, {}, ResponseStatus.fail(), None),
        (
            "test_403_ignore_error_message",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(action=ResponseAction.IGNORE, error_message_contain="found"),
            {},
            ResponseStatus.ignore(),
            None,
        ),
        (
            "test_403_dont_ignore_error_message",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(action=ResponseAction.IGNORE, error_message_contain="not_found"),
            {},
            ResponseStatus.fail(),
            None,
        ),
        ("test_429", HTTPStatus.TOO_MANY_REQUESTS, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_ignore_403",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={HTTPStatus.FORBIDDEN}),
            {},
            ResponseStatus.ignore(),
            None,
        ),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(action=ResponseAction.RETRY, predicate="{{ 'code' in decoded_response }}"),
            None,
            {},
            ResponseStatus.retry(10),
            None,
        ),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(action=ResponseAction.RETRY, predicate="{{ 'some_absent_field' in decoded_response }}"),
            None,
            {},
            ResponseStatus.fail(),
            None,
        ),
        (
            "test_retry_403",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(action=ResponseAction.RETRY, http_codes={HTTPStatus.FORBIDDEN}),
            None,
            {},
            ResponseStatus.retry(10),
            None,
        ),
    ],
)
def test_default_retrier(
    test_name, http_code, retry_response_filter, ignore_response_filter, response_headers, should_retry, backoff_strategy
):
    response_mock = create_response(http_code, headers=response_headers, json_body={"code": "1000", "error": "found"})
    response_mock.ok = http_code < 400
    response_filters = [f for f in [retry_response_filter, ignore_response_filter] if f]
    retrier = DefaultErrorHandler(response_filters=response_filters, backoff_strategies=backoff_strategy)
    actual_should_retry = retrier.should_retry(response_mock)
    assert actual_should_retry == should_retry
    if should_retry.action == ResponseAction.RETRY:
        assert actual_should_retry.retry_in == should_retry.retry_in


def test_default_retrier_attempt_count_increases():
    status_code = 500
    response_mock = create_response(status_code)
    retrier = DefaultErrorHandler()
    actual_should_retry = retrier.should_retry(response_mock)
    assert actual_should_retry == ResponseStatus.retry(10)
    assert actual_should_retry.retry_in == 10

    # This is the same request, so the count should increase
    actual_should_retry = retrier.should_retry(response_mock)
    assert actual_should_retry == ResponseStatus.retry(20)
    assert actual_should_retry.retry_in == 20

    # This is a different request, so the count should not increase
    another_identical_request = create_response(status_code)
    actual_should_retry = retrier.should_retry(another_identical_request)
    assert actual_should_retry == ResponseStatus.retry(10)
    assert actual_should_retry.retry_in == 10


def create_response(status_code: int, headers=None, json_body=None):
    url = "https://airbyte.io"

    response_mock = MagicMock()
    response_mock.status_code = status_code
    response_mock.ok = status_code < 400 or status_code >= 600
    response_mock.url = url
    response_mock.headers = headers or {}
    response_mock.json.return_value = json_body or {}
    return response_mock


@pytest.mark.parametrize(
    "test_name, first_retrier_behavior, second_retrier_behavior, expected_behavior",
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
def test_chain_retrier(test_name, first_retrier_behavior, second_retrier_behavior, expected_behavior):
    first_retier = MagicMock()
    first_retier.should_retry.return_value = first_retrier_behavior
    second_retrier = MagicMock()
    second_retrier.should_retry.return_value = second_retrier_behavior
    second_retrier.should_retry.return_value = second_retrier_behavior
    retriers = [first_retier, second_retrier]
    retrier = CompositeErrorHandler(retriers)
    response_mock = MagicMock()
    response_mock.ok = first_retrier_behavior == ResponseStatus.success() or second_retrier_behavior == ResponseStatus.success()
    assert retrier.should_retry(response_mock) == expected_behavior


@pytest.mark.parametrize(
    "test_name, header, header_value, regex, expected_backoff_time",
    [
        ("test_wait_time_from_header", "wait_time", SOME_BACKOFF_TIME, None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_string", "wait_time", "60", None, SOME_BACKOFF_TIME),
        ("test_wait_time_from_header_not_a_number", "wait_time", "61,60", None, None),
        ("test_wait_time_from_header_with_regex", "wait_time", "61,60", "([-+]?\d+)", 61),  # noqa
        ("test_wait_time_from_header_with_regex_no_match", "wait_time", "...", "[-+]?\d+", None),  # noqa
        ("test_wait_time_from_header", "absent_header", None, None, None),
    ],
)
def test_wait_time_from_header(test_name, header, header_value, regex, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.headers = {"wait_time": header_value}
    backoff_stratery = WaitTimeFromHeaderBackoffStrategy(header, regex)
    backoff = backoff_stratery.backoff(response_mock, 1)
    assert backoff == expected_backoff_time


@pytest.mark.parametrize(
    "test_name, header, wait_until, min_wait, regex, expected_backoff_time",
    [
        ("test_wait_until_time_from_header", "wait_until", 1600000060.0, None, None, 60),
        ("test_wait_until_negative_time", "wait_until", 1500000000.0, None, None, None),
        ("test_wait_until_time_less_than_min", "wait_until", 1600000060.0, 120, None, 120),
        ("test_wait_until_no_header", "absent_header", 1600000000.0, None, None, None),
        ("test_wait_until_time_from_header_not_numeric", "wait_until", "1600000000,1600000000", None, None, None),
        ("test_wait_until_time_from_header_is_numeric", "wait_until", "1600000060", None, None, 60),
        ("test_wait_until_time_from_header_with_regex", "wait_until", "1600000060,60", None, "[-+]?\d+", 60),  # noqa
        ("test_wait_until_time_from_header_with_regex_no_match", "wait_time", "...", None, "[-+]?\d+", None),  # noqa
        ("test_wait_until_no_header_with_min", "absent_header", "1600000000.0", SOME_BACKOFF_TIME, None, SOME_BACKOFF_TIME),
    ],
)
@patch("time.time", return_value=1600000000.0)
def test_wait_untiltime_from_header(time_mock, test_name, header, wait_until, min_wait, regex, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.headers = {"wait_until": wait_until}
    backoff_stratery = WaitUntilTimeFromHeaderBackoffStrategy(header, min_wait, regex)
    backoff = backoff_stratery.backoff(response_mock, 1)
    assert backoff == expected_backoff_time


@pytest.mark.parametrize(
    "test_name, attempt_count, expected_backoff_time",
    [
        ("test_exponential_backoff", 1, 10),
        ("test_exponential_backoff", 2, 20),
    ],
)
def test_exponential_backoff(test_name, attempt_count, expected_backoff_time):
    response_mock = MagicMock()
    backoff_stratery = ExponentialBackoffStrategy(factor=5)
    backoff = backoff_stratery.backoff(response_mock, attempt_count)
    assert backoff == expected_backoff_time
