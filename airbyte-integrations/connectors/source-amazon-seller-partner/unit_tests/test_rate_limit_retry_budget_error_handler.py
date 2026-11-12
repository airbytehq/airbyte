#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import threading
from unittest.mock import patch

import pytest
import requests
from components import RateLimitRetryBudgetErrorHandler

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


_URL = "https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/amzn1.spdoc.1.done"
_OTHER_URL = "https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/amzn1.spdoc.1.other"


def _handler(other_errors_max_retries: int = 2, other_errors_max_time: int = 600) -> RateLimitRetryBudgetErrorHandler:
    return RateLimitRetryBudgetErrorHandler(
        config={},
        parameters={},
        response_filters=[
            HttpResponseFilter(config={}, parameters={}, action="RETRY", http_codes={429}),
            HttpResponseFilter(config={}, parameters={}, action="RETRY", http_codes={403}),
        ],
        max_retries=30,
        max_time=3600,
        other_errors_max_retries=other_errors_max_retries,
        other_errors_max_time=other_errors_max_time,
    )


def _response(status_code: int, url: str = _URL) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = b""
    # A new request object per response, as HTTP mocking libraries do, so tracking cannot rely on object identity.
    response.request = requests.Request("GET", url).prepare()
    return response


def _actions(handler: RateLimitRetryBudgetErrorHandler, responses: list) -> list[ResponseAction]:
    return [handler.interpret_response(response).response_action for response in responses]


def test_given_handler_then_http_client_gets_the_429_budget() -> None:
    handler = _handler()

    assert handler.max_retries == 30
    assert handler.max_time == 3600


@pytest.mark.parametrize("status_code", [403, 500, 503])
def test_given_other_error_beyond_its_retry_limit_then_fail(status_code: int) -> None:
    assert _actions(_handler(), [_response(status_code)] * 3) == [ResponseAction.RETRY, ResponseAction.RETRY, ResponseAction.FAIL]


def test_given_429s_then_never_failed_by_this_handler() -> None:
    assert set(_actions(_handler(), [_response(429)] * 40)) == {ResponseAction.RETRY}


def test_given_429s_between_other_errors_then_429s_do_not_count_toward_other_error_limit() -> None:
    responses = [_response(403), *[_response(429)] * 10, _response(403), _response(429), _response(403)]

    assert _actions(_handler(), responses)[-3:] == [ResponseAction.RETRY, ResponseAction.RETRY, ResponseAction.FAIL]


def test_given_connection_error_then_counts_as_other_error() -> None:
    request = requests.Request("GET", _URL).prepare()
    errors = [requests.ConnectionError("connection reset", request=request) for _ in range(3)]

    assert _actions(_handler(), errors) == [ResponseAction.RETRY, ResponseAction.RETRY, ResponseAction.FAIL]


def test_given_other_error_after_its_time_limit_then_fail() -> None:
    handler = _handler(other_errors_max_retries=10, other_errors_max_time=600)

    with patch("components.time.monotonic", side_effect=[1000.0, 1600.0, 1601.0]):
        actions = _actions(handler, [_response(403)] * 3)

    assert actions == [ResponseAction.RETRY, ResponseAction.RETRY, ResponseAction.FAIL]


def test_given_success_then_next_request_gets_a_fresh_other_error_limit() -> None:
    handler = _handler()
    _actions(handler, [_response(403), _response(403), _response(200)])

    assert _actions(handler, [_response(403), _response(403)]) == [ResponseAction.RETRY, ResponseAction.RETRY]


def test_given_failure_then_next_request_to_same_url_gets_a_fresh_other_error_limit() -> None:
    handler = _handler()
    _actions(handler, [_response(403)] * 3)

    assert _actions(handler, [_response(403), _response(403)]) == [ResponseAction.RETRY, ResponseAction.RETRY]


def test_given_other_url_then_tracked_separately() -> None:
    handler = _handler()
    _actions(handler, [_response(403), _response(403)])

    assert _actions(handler, [_response(403, _OTHER_URL), _response(403, _OTHER_URL)]) == [ResponseAction.RETRY, ResponseAction.RETRY]


def test_given_requests_on_two_threads_then_tracked_separately() -> None:
    handler = _handler()
    _actions(handler, [_response(403), _response(403)])
    other_thread_actions = []
    thread = threading.Thread(target=lambda: other_thread_actions.extend(_actions(handler, [_response(403), _response(403)])))
    thread.start()
    thread.join()

    assert other_thread_actions == [ResponseAction.RETRY, ResponseAction.RETRY]
    assert _actions(handler, [_response(403)]) == [ResponseAction.FAIL]


def test_given_limit_exhausted_then_fail_resolution_explains_limit_and_keeps_failure_type() -> None:
    handler = _handler()
    resolution = [handler.interpret_response(_response(500)) for _ in range(3)][-1]

    assert resolution.failure_type == FailureType.transient_error
    assert "limit 2 retries / 600s for errors other than 429" in resolution.error_message
