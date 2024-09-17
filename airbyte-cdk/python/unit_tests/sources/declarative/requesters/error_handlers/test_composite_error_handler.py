#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction

SOME_BACKOFF_TIME = 60


@pytest.mark.parametrize(
    "test_name, first_handler_behavior, second_handler_behavior, expected_behavior",
    [
        (
            "test_chain_retrier_ok_ok",
            ErrorResolution(
                response_action=ResponseAction.SUCCESS,
                failure_type=None,
                error_message=None,
            ),
            ErrorResolution(
                response_action=ResponseAction.SUCCESS,
                failure_type=None,
                error_message=None,
            ),
            ErrorResolution(
                response_action=ResponseAction.SUCCESS,
                failure_type=None,
                error_message=None,
            ),
        ),
        (
            "test_chain_retrier_ignore_fail",
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
            ErrorResolution(
                response_action=ResponseAction.FAIL,
            ),
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
        ),
        (
            "test_chain_retrier_fail_ignore",
            ErrorResolution(
                response_action=ResponseAction.FAIL,
            ),
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
        ),
        (
            "test_chain_retrier_ignore_retry",
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
            ErrorResolution(
                response_action=ResponseAction.RETRY,
            ),
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
        ),
        (
            "test_chain_retrier_ignore_success",
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
            ErrorResolution(
                response_action=ResponseAction.SUCCESS,
            ),
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
            ),
        ),
    ],
)
def test_composite_error_handler(test_name, first_handler_behavior, second_handler_behavior, expected_behavior):
    first_error_handler = MagicMock()
    first_error_handler.interpret_response.return_value = first_handler_behavior
    second_error_handler = MagicMock()
    second_error_handler.interpret_response.return_value = second_handler_behavior
    retriers = [first_error_handler, second_error_handler]
    retrier = CompositeErrorHandler(error_handlers=retriers, parameters={})
    response_mock = MagicMock()
    response_mock.ok = first_handler_behavior.response_action == ResponseAction.SUCCESS or second_handler_behavior == ResponseAction.SUCCESS
    assert retrier.interpret_response(response_mock) == expected_behavior


def test_given_unmatched_response_or_exception_then_return_default_error_resolution():
    composite_error_handler = CompositeErrorHandler(
        error_handlers=[
            DefaultErrorHandler(
                response_filters=[],
                parameters={},
                config={},
            )
        ],
        parameters={},
    )

    error_resolution = composite_error_handler.interpret_response(ValueError("Any error"))

    assert error_resolution.response_action == ResponseAction.RETRY
    assert error_resolution.failure_type == FailureType.system_error


def test_composite_error_handler_no_handlers():
    try:
        CompositeErrorHandler(error_handlers=[], parameters={})
        assert False
    except ValueError:
        pass


def test_error_handler_compatibility_simple():
    status_code = 403
    expected_action = ResponseAction.IGNORE
    response_mock = create_response(status_code)
    default_error_handler = DefaultErrorHandler(
        config={},
        parameters={},
        response_filters=[HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={403}, config={}, parameters={})],
    )
    composite_error_handler = CompositeErrorHandler(
        error_handlers=[
            DefaultErrorHandler(
                response_filters=[HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={403}, parameters={}, config={})],
                parameters={},
                config={},
            )
        ],
        parameters={},
    )
    assert default_error_handler.interpret_response(response_mock).response_action == expected_action
    assert composite_error_handler.interpret_response(response_mock).response_action == expected_action


@pytest.mark.parametrize(
    "test_name, status_code, expected_action",
    [("test_first_filter", 403, ResponseAction.IGNORE), ("test_second_filter", 404, ResponseAction.FAIL)],
)
def test_error_handler_compatibility_multiple_filters(test_name, status_code, expected_action):
    response_mock = create_response(status_code)
    error_handler_with_multiple_filters = CompositeErrorHandler(
        error_handlers=[
            DefaultErrorHandler(
                response_filters=[
                    HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={403}, parameters={}, config={}),
                    HttpResponseFilter(action=ResponseAction.FAIL, http_codes={404}, parameters={}, config={}),
                ],
                parameters={},
                config={},
            ),
        ],
        parameters={},
    )
    composite_error_handler_with_single_filters = CompositeErrorHandler(
        error_handlers=[
            DefaultErrorHandler(
                response_filters=[HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={403}, parameters={}, config={})],
                parameters={},
                config={},
            ),
            DefaultErrorHandler(
                response_filters=[HttpResponseFilter(action=ResponseAction.FAIL, http_codes={404}, parameters={}, config={})],
                parameters={},
                config={},
            ),
        ],
        parameters={},
    )
    actual_action_multiple_filters = error_handler_with_multiple_filters.interpret_response(response_mock).response_action
    assert actual_action_multiple_filters == expected_action

    actual_action_single_filters = composite_error_handler_with_single_filters.interpret_response(response_mock).response_action
    assert actual_action_single_filters == expected_action


def create_response(status_code: int, headers=None, json_body=None):
    url = "https://airbyte.io"

    response_mock = MagicMock(spec=requests.Response)
    response_mock.request = MagicMock(spec=requests.PreparedRequest)
    response_mock.status_code = status_code
    response_mock.ok = status_code < 400 or status_code >= 600
    response_mock.url = url
    response_mock.headers = headers or {}
    response_mock.json.return_value = json_body or {}
    return response_mock


@pytest.mark.parametrize(
    "test_name, max_times, expected_max_time",
    [
        ("test_single_handler", [10], 10),
        ("test_multiple_handlers", [10, 15], 15),
    ],
)
def test_max_time_is_max_of_underlying_handlers(test_name, max_times, expected_max_time):
    composite_error_handler = CompositeErrorHandler(
        error_handlers=[
            DefaultErrorHandler(
                response_filters=[HttpResponseFilter(action=ResponseAction.IGNORE, http_codes={403}, parameters={}, config={})],
                max_time=max_time,
                parameters={},
                config={},
            )
            for max_time in max_times
        ],
        parameters={},
    )

    max_time = composite_error_handler.max_time
    assert max_time == expected_max_time
