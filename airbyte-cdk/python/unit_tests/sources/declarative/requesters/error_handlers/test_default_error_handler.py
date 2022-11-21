#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import airbyte_cdk.sources.declarative.requesters.error_handlers.response_status as response_status
import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import (
    DefaultErrorHandler,
    HttpResponseFilter,
    ResponseStatus,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, http_code, retry_response_filter, ignore_response_filter, response_headers, should_retry, backoff_strategy",
    [
        ("test_bad_gateway", HTTPStatus.BAD_GATEWAY, None, None, {}, ResponseStatus.retry(10), None),
        ("test_too_many_requests", HTTPStatus.TOO_MANY_REQUESTS, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_bad_gateway_constant_retry",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            ResponseStatus.retry(SOME_BACKOFF_TIME),
            [ConstantBackoffStrategy(options={}, backoff_time_in_seconds=SOME_BACKOFF_TIME, config={})],
        ),
        ("test_exponential_backoff", HTTPStatus.BAD_GATEWAY, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_bad_gateway_exponential_backoff_explicit_parameter",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            ResponseStatus.retry(10),
            [DefaultErrorHandler.DEFAULT_BACKOFF_STRATEGY(options={}, config={})],
        ),
        ("test_chain_backoff_strategy", HTTPStatus.BAD_GATEWAY, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_bad_gateway_chain_backoff",
            HTTPStatus.BAD_GATEWAY,
            None,
            None,
            {},
            ResponseStatus.retry(10),
            [
                DefaultErrorHandler.DEFAULT_BACKOFF_STRATEGY(options={}, config={}),
                ConstantBackoffStrategy(options={}, backoff_time_in_seconds=SOME_BACKOFF_TIME, config={}),
            ],
        ),
        ("test_200", HTTPStatus.OK, None, None, {}, response_status.SUCCESS, None),
        ("test_3XX", HTTPStatus.PERMANENT_REDIRECT, None, None, {}, response_status.SUCCESS, None),
        ("test_403", HTTPStatus.FORBIDDEN, None, None, {}, response_status.FAIL, None),
        (
            "test_403_ignore_error_message",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(action=ResponseAction.IGNORE, error_message_contains="found", config={}, options={}),
            {},
            response_status.IGNORE,
            None,
        ),
        (
            "test_403_dont_ignore_error_message",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(action=ResponseAction.IGNORE, error_message_contains="not_found", config={}, options={}),
            {},
            response_status.FAIL,
            None,
        ),
        ("test_429", HTTPStatus.TOO_MANY_REQUESTS, None, None, {}, ResponseStatus.retry(10), None),
        (
            "test_ignore_403",
            HTTPStatus.FORBIDDEN,
            None,
            HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={HTTPStatus.FORBIDDEN}, config={}, options={}),
            {},
            response_status.IGNORE,
            None,
        ),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(action=ResponseAction.RETRY, predicate="{{ 'code' in response }}", config={}, options={}),
            None,
            {},
            ResponseStatus.retry(10),
            None,
        ),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(action=ResponseAction.RETRY, predicate="{{ 'some_absent_field' in response }}", config={}, options={}),
            None,
            {},
            response_status.FAIL,
            None,
        ),
        (
            "test_200_fail_with_predicate",
            HTTPStatus.OK,
            HttpResponseFilter(action=ResponseAction.FAIL, error_message_contains="found", config={}, options={}),
            None,
            {},
            response_status.FAIL,
            None,
        ),
        (
            "test_retry_403",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(action=ResponseAction.RETRY, http_codes={HTTPStatus.FORBIDDEN}, config={}, options={}),
            None,
            {},
            ResponseStatus.retry(10),
            None,
        ),
        (
            "test_200_fail_with_predicate_from_header",
            HTTPStatus.OK,
            HttpResponseFilter(action=ResponseAction.FAIL, predicate="{{ headers['fail'] }}", config={}, options={}),
            None,
            {"fail": True},
            response_status.FAIL,
            None,
        ),
    ],
)
def test_default_error_handler(
    test_name, http_code, retry_response_filter, ignore_response_filter, response_headers, should_retry, backoff_strategy
):
    response_mock = create_response(http_code, headers=response_headers, json_body={"code": "1000", "error": "found"})
    response_mock.ok = http_code < 400
    response_filters = [f for f in [retry_response_filter, ignore_response_filter] if f]
    error_handler = DefaultErrorHandler(response_filters=response_filters, backoff_strategies=backoff_strategy, config={}, options={})
    actual_should_retry = error_handler.interpret_response(response_mock)
    assert actual_should_retry == should_retry
    if should_retry.action == ResponseAction.RETRY:
        assert actual_should_retry.retry_in == should_retry.retry_in


def test_default_error_handler_attempt_count_increases():
    status_code = 500
    response_mock = create_response(status_code)
    error_handler = DefaultErrorHandler(config={}, options={})
    actual_should_retry = error_handler.interpret_response(response_mock)
    assert actual_should_retry == ResponseStatus.retry(10)
    assert actual_should_retry.retry_in == 10

    # This is the same request, so the count should increase
    actual_should_retry = error_handler.interpret_response(response_mock)
    assert actual_should_retry == ResponseStatus.retry(20)
    assert actual_should_retry.retry_in == 20

    # This is a different request, so the count should not increase
    another_identical_request = create_response(status_code)
    actual_should_retry = error_handler.interpret_response(another_identical_request)
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
