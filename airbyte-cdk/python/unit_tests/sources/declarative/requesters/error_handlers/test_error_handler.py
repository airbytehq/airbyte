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
from airbyte_cdk.sources.declarative.requesters.error_handlers.chain_retrier import ChainRetrier
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_retrier import (
    DefaultRetrier,
    HttpResponseFilter,
    NonRetriableResponseStatus,
    RetryResponseStatus,
)

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, http_code, retry_response_filter, ignore_response_filter, response_headers, should_retry, backoff_strategy",
    [
        ("test_bad_gateway", HTTPStatus.BAD_GATEWAY, None, None, {}, RetryResponseStatus(10), None),
        (
            "test_bad_gateway_constant_retry",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            RetryResponseStatus(SOME_BACKOFF_TIME),
            [ConstantBackoffStrategy(SOME_BACKOFF_TIME)],
        ),
        ("test_exponential_backoff", HTTPStatus.BAD_GATEWAY, None, None, {}, RetryResponseStatus(10), None),
        (
            "test_bad_gateway_exponential_backoff_explicit_parameter",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            RetryResponseStatus(10),
            [DefaultRetrier.DEFAULT_BACKOFF_STRATEGY()],
        ),
        ("test_chain_backoff_strategy", HTTPStatus.BAD_GATEWAY, None, None, {}, RetryResponseStatus(10), None),
        (
            "test_bad_gateway_chain_backoff",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            RetryResponseStatus(10),
            [DefaultRetrier.DEFAULT_BACKOFF_STRATEGY(), ConstantBackoffStrategy(SOME_BACKOFF_TIME)],
        ),
        ("test_200", HTTPStatus.OK, None, None, {}, NonRetriableResponseStatus.SUCCESS, None),
        ("test_3XX", HTTPStatus.PERMANENT_REDIRECT, None, None, {}, NonRetriableResponseStatus.SUCCESS, None),
        ("test_403", HTTPStatus.FORBIDDEN, None, None, {}, NonRetriableResponseStatus.FAIL, None),
        (
            "test_403_ignore_error_message",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(error_message_contain="found"),
            {},
            NonRetriableResponseStatus.IGNORE,
            None,
        ),
        (
            "test_403_dont_ignore_error_message",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(error_message_contain="not_found"),
            {},
            NonRetriableResponseStatus.FAIL,
            None,
        ),
        ("test_429", HTTPStatus.TOO_MANY_REQUESTS, None, None, {}, RetryResponseStatus(10), None),
        (
            "test_ignore_403",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(http_codes={HTTPStatus.FORBIDDEN}),
            {},
            NonRetriableResponseStatus.IGNORE,
            None,
        ),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(predicate="{{ 'code' in decoded_response }}"),
            None,
            {},
            RetryResponseStatus(10),
            None,
        ),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(predicate="{{ 'some_absent_field' in decoded_response }}"),
            None,
            {},
            NonRetriableResponseStatus.FAIL,
            None,
        ),
        (
            "test_retry_403",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter({HTTPStatus.FORBIDDEN}),
            None,
            {},
            RetryResponseStatus(10),
            None,
        ),
    ],
)
def test_default_retrier(
    test_name, http_code, retry_response_filter, ignore_response_filter, response_headers, should_retry, backoff_strategy
):
    response_mock = create_response(http_code, headers=response_headers, json_body={"code": "1000", "error": "found"})
    response_mock.ok = http_code < 400
    retrier = DefaultRetrier(
        retry_response_filter=retry_response_filter, ignore_response_filter=ignore_response_filter, backoff_strategy=backoff_strategy
    )
    actual_should_retry = retrier.should_retry(response_mock)
    assert actual_should_retry == should_retry
    if isinstance(should_retry, RetryResponseStatus):
        assert actual_should_retry.retry_in == should_retry.retry_in


def test_default_retrier_attempt_count_increases():
    status_code = 500
    response_mock = create_response(status_code)
    retrier = DefaultRetrier()
    actual_should_retry = retrier.should_retry(response_mock)
    assert actual_should_retry == RetryResponseStatus(10)
    assert actual_should_retry.retry_in == 10

    # This is the same request, so the count should increase
    actual_should_retry = retrier.should_retry(response_mock)
    assert actual_should_retry == RetryResponseStatus(20)
    assert actual_should_retry.retry_in == 20

    # This is a different request, so the count should not increase
    another_identical_request = create_response(status_code)
    actual_should_retry = retrier.should_retry(another_identical_request)
    assert actual_should_retry == RetryResponseStatus(10)
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
            NonRetriableResponseStatus.SUCCESS,
            NonRetriableResponseStatus.SUCCESS,
            NonRetriableResponseStatus.SUCCESS,
        ),
        (
            "test_chain_retrier_ignore_fail",
            NonRetriableResponseStatus.IGNORE,
            NonRetriableResponseStatus.FAIL,
            NonRetriableResponseStatus.IGNORE,
        ),
        (
            "test_chain_retrier_fail_ignore",
            NonRetriableResponseStatus.FAIL,
            NonRetriableResponseStatus.IGNORE,
            NonRetriableResponseStatus.IGNORE,
        ),
        (
            "test_chain_retrier_ignore_retry",
            NonRetriableResponseStatus.IGNORE,
            RetryResponseStatus(SOME_BACKOFF_TIME),
            NonRetriableResponseStatus.IGNORE,
        ),
        (
            "test_chain_retrier_retry_ignore",
            RetryResponseStatus(SOME_BACKOFF_TIME),
            NonRetriableResponseStatus.IGNORE,
            NonRetriableResponseStatus.IGNORE,
        ),
        (
            "test_chain_retrier_retry_fail",
            RetryResponseStatus(SOME_BACKOFF_TIME),
            NonRetriableResponseStatus.FAIL,
            RetryResponseStatus(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_fail_retry",
            NonRetriableResponseStatus.FAIL,
            RetryResponseStatus(SOME_BACKOFF_TIME),
            RetryResponseStatus(SOME_BACKOFF_TIME),
        ),
        (
            "test_chain_retrier_ignore_ok",
            NonRetriableResponseStatus.IGNORE,
            NonRetriableResponseStatus.SUCCESS,
            NonRetriableResponseStatus.SUCCESS,
        ),
        (
            "test_chain_retrier_ok_ignore",
            NonRetriableResponseStatus.SUCCESS,
            NonRetriableResponseStatus.IGNORE,
            NonRetriableResponseStatus.SUCCESS,
        ),
        (
            "test_chain_retrier_ok_retry",
            NonRetriableResponseStatus.SUCCESS,
            RetryResponseStatus(SOME_BACKOFF_TIME),
            NonRetriableResponseStatus.SUCCESS,
        ),
        (
            "test_chain_retrier_retry_ok",
            RetryResponseStatus(SOME_BACKOFF_TIME),
            NonRetriableResponseStatus.SUCCESS,
            NonRetriableResponseStatus.SUCCESS,
        ),
        (
            "test_chain_retrier_return_first_retry",
            RetryResponseStatus(SOME_BACKOFF_TIME),
            RetryResponseStatus(2 * SOME_BACKOFF_TIME),
            RetryResponseStatus(SOME_BACKOFF_TIME),
        ),
    ],
)
def test_chain_retrier_first_retrier_ignores_second_fails(test_name, first_retrier_behavior, second_retrier_behavior, expected_behavior):
    first_retier = MagicMock()
    first_retier.should_retry.return_value = first_retrier_behavior
    second_retrier = MagicMock()
    second_retrier.should_retry.return_value = second_retrier_behavior
    second_retrier.should_retry.return_value = second_retrier_behavior
    retriers = [first_retier, second_retrier]
    retrier = ChainRetrier(retriers)
    response_mock = MagicMock()
    response_mock.ok = (
        first_retrier_behavior == NonRetriableResponseStatus.SUCCESS or second_retrier_behavior == NonRetriableResponseStatus.SUCCESS
    )
    assert retrier.should_retry(response_mock) == expected_behavior


@pytest.mark.parametrize(
    "test_name, header, expected_backoff_time",
    [("test_wait_time_from_header", "wait_time", SOME_BACKOFF_TIME), ("test_wait_time_from_header", "absent_header", None)],
)
def test_wait_time_from_header(test_name, header, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.headers = {"wait_time": SOME_BACKOFF_TIME}
    backoff_stratery = WaitTimeFromHeaderBackoffStrategy(header)
    backoff = backoff_stratery.backoff(response_mock, 1)
    assert backoff == expected_backoff_time


@pytest.mark.parametrize(
    "test_name, header, wait_until, min_wait, expected_backoff_time",
    [
        ("test_wait_until_time_from_header", "wait_until", 1600000060.0, None, SOME_BACKOFF_TIME),
        ("test_wait_until_negative_time", "wait_until", 1500000000.0, None, None),
        ("test_wait_until_time_less_than_min", "wait_until", 1600000060.0, 120, 120),
        ("test_wait_until_no_header", "absent_header", 1600000000.0, None, None),
        ("test_wait_until_no_header_with_min", "absent_header", 1600000000.0, SOME_BACKOFF_TIME, SOME_BACKOFF_TIME),
    ],
)
@patch("time.time", return_value=1600000000.0)
def test_wait_untiltime_from_header(time_mock, test_name, header, wait_until, min_wait, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.headers = {"wait_until": wait_until}
    backoff_stratery = WaitUntilTimeFromHeaderBackoffStrategy(header, min_wait)
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
