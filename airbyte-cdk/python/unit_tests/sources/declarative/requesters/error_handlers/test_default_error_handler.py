#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler, HttpResponseFilter
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, http_status_code, expected_error_resolution",
    [
        (
            "_with_http_response_status_200",
            200,
            ErrorResolution(
                response_action=ResponseAction.SUCCESS,
                failure_type=None,
                error_message=None,
            ),
        ),
        (
            "_with_http_response_status_400",
            400,
            DEFAULT_ERROR_MAPPING[400],
        ),
        (
            "_with_http_response_status_404",
            404,
            DEFAULT_ERROR_MAPPING[404],
        ),
        (
            "_with_http_response_status_408",
            408,
            DEFAULT_ERROR_MAPPING[408],
        ),
        (
            "_with_unmapped_http_status_418",
            418,
            ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.system_error,
                error_message="Unexpected response with HTTP status 418",
            ),
        ),
    ],
)
def test_default_error_handler_with_default_response_filter(test_name, http_status_code: int, expected_error_resolution: ErrorResolution):
    response_mock = create_response(http_status_code)
    error_handler = DefaultErrorHandler(config={}, parameters={})
    actual_error_resolution = error_handler.interpret_response(response_mock)
    assert actual_error_resolution.response_action == expected_error_resolution.response_action
    assert actual_error_resolution.failure_type == expected_error_resolution.failure_type
    assert actual_error_resolution.error_message == expected_error_resolution.error_message


@pytest.mark.parametrize(
    "test_name, http_status_code, test_response_filter, response_action, failure_type, error_message",
    [
        (
            "_with_http_response_status_400_fail_with_default_failure_type",
            400,
            HttpResponseFilter(
                http_codes=[400],
                action=ResponseAction.RETRY,
                config={},
                parameters={},
            ),
            ResponseAction.RETRY,
            FailureType.system_error,
            "Bad request. Please check your request parameters.",
        ),
        (
            "_with_http_response_status_402_fail_with_default_failure_type",
            402,
            HttpResponseFilter(
                http_codes=[402],
                action=ResponseAction.FAIL,
                config={},
                parameters={},
            ),
            ResponseAction.FAIL,
            FailureType.system_error,
            "",
        ),
        (
            "_with_http_response_status_403_fail_with_default_failure_type",
            403,
            HttpResponseFilter(
                http_codes=[403],
                action="FAIL",
                config={},
                parameters={},
            ),
            ResponseAction.FAIL,
            FailureType.config_error,
            "Forbidden. You don't have permission to access this resource.",
        ),
        (
            "_with_http_response_status_200_fail_with_contained_error_message",
            418,
            HttpResponseFilter(
                action=ResponseAction.FAIL,
                error_message_contains="test",
                config={},
                parameters={},
            ),
            ResponseAction.FAIL,
            FailureType.system_error,
            "",
        ),
        (
            "_fail_with_predicate",
            418,
            HttpResponseFilter(
                action=ResponseAction.FAIL,
                predicate="{{ 'error' in response }}",
                config={},
                parameters={},
            ),
            ResponseAction.FAIL,
            FailureType.system_error,
            "",
        ),
    ],
)
def test_default_error_handler_with_custom_response_filter(
    test_name, http_status_code, test_response_filter, response_action, failure_type, error_message
):
    response_mock = create_response(http_status_code)
    if http_status_code == 418:
        response_mock.json.return_value = {"error": "test"}

    response_filter = test_response_filter
    error_handler = DefaultErrorHandler(config={}, parameters={}, response_filters=[response_filter])
    actual_error_resolution = error_handler.interpret_response(response_mock)
    assert actual_error_resolution.response_action == response_action
    assert actual_error_resolution.failure_type == failure_type
    assert actual_error_resolution.error_message == error_message


@pytest.mark.parametrize(
    "http_status_code, expected_response_action",
    [
        (400, ResponseAction.RETRY),
        (402, ResponseAction.FAIL),
    ],
)
def test_default_error_handler_with_multiple_response_filters(http_status_code, expected_response_action):
    response_filter_one = HttpResponseFilter(
        http_codes=[400],
        action=ResponseAction.RETRY,
        config={},
        parameters={},
    )
    response_filter_two = HttpResponseFilter(
        http_codes=[402],
        action=ResponseAction.FAIL,
        config={},
        parameters={},
    )

    response_mock = create_response(http_status_code)
    error_handler = DefaultErrorHandler(config={}, parameters={}, response_filters=[response_filter_one, response_filter_two])
    actual_error_resolution = error_handler.interpret_response(response_mock)
    assert actual_error_resolution.response_action == expected_response_action


@pytest.mark.parametrize(
    "first_response_filter_action, second_response_filter_action, expected_response_action",
    [
        (ResponseAction.RETRY, ResponseAction.FAIL, ResponseAction.RETRY),
        (ResponseAction.FAIL, ResponseAction.RETRY, ResponseAction.FAIL),
        (ResponseAction.IGNORE, ResponseAction.IGNORE, ResponseAction.IGNORE),
        (ResponseAction.SUCCESS, ResponseAction.IGNORE, ResponseAction.SUCCESS),
    ],
)
def test_default_error_handler_with_conflicting_response_filters(
    first_response_filter_action, second_response_filter_action, expected_response_action
):
    response_filter_one = HttpResponseFilter(
        http_codes=[400],
        action=first_response_filter_action,
        config={},
        parameters={},
    )
    response_filter_two = HttpResponseFilter(
        http_codes=[400],
        action=second_response_filter_action,
        config={},
        parameters={},
    )

    response_mock = create_response(400)
    error_handler = DefaultErrorHandler(config={}, parameters={}, response_filters=[response_filter_one, response_filter_two])
    actual_error_resolution = error_handler.interpret_response(response_mock)
    assert actual_error_resolution.response_action == expected_response_action


def test_default_error_handler_with_constant_backoff_strategy():
    response_mock = create_response(429)
    error_handler = DefaultErrorHandler(
        config={}, parameters={}, backoff_strategies=[ConstantBackoffStrategy(SOME_BACKOFF_TIME, config={}, parameters={})]
    )
    assert error_handler.backoff_time(response_or_exception=response_mock, attempt_count=0) == SOME_BACKOFF_TIME


@pytest.mark.parametrize(
    "attempt_count",
    [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
    ],
)
def test_default_error_handler_with_exponential_backoff_strategy(attempt_count):
    response_mock = create_response(429)
    error_handler = DefaultErrorHandler(
        config={}, parameters={}, backoff_strategies=[ExponentialBackoffStrategy(factor=1, config={}, parameters={})]
    )
    assert error_handler.backoff_time(response_or_exception=response_mock, attempt_count=attempt_count) == (1 * 2**attempt_count)


def create_response(status_code: int, headers=None, json_body=None):
    url = "https://airbyte.io"

    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = status_code
    response_mock.ok = status_code < 400 or status_code >= 600
    response_mock.url = url
    response_mock.headers = headers or {}
    response_mock.json.return_value = json_body or {}
    response_mock.request = MagicMock(spec=requests.PreparedRequest)
    return response_mock


def test_default_error_handler_with_unmapped_http_code():
    error_handler = DefaultErrorHandler(config={}, parameters={})
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = 418
    response_mock.ok = False
    response_mock.headers = {}
    actual_error_resolution = error_handler.interpret_response(response_mock)
    assert actual_error_resolution
    assert actual_error_resolution.failure_type == FailureType.system_error
    assert actual_error_resolution.response_action == ResponseAction.RETRY


def test_predicate_takes_precedent_over_default_mapped_error():
    response_mock = create_response(404, json_body={"error": "test"})

    response_filter = HttpResponseFilter(
        action=ResponseAction.FAIL,
        predicate="{{ 'error' in response }}",
        config={},
        parameters={},
    )

    error_handler = DefaultErrorHandler(config={}, parameters={}, response_filters=[response_filter])
    actual_error_resolution = error_handler.interpret_response(response_mock)
    assert actual_error_resolution.response_action == ResponseAction.FAIL
    assert actual_error_resolution.failure_type == FailureType.system_error
    assert actual_error_resolution.error_message == DEFAULT_ERROR_MAPPING.get(404).error_message
