#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.error_handlers import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus


@pytest.mark.parametrize(
    "action, http_codes, predicate, error_contains, back_off, error_message, response, expected_response_status",
    [
        pytest.param(
            ResponseAction.FAIL,
            {501, 503},
            "",
            "",
            None,
            "custom error message",
            {"status_code": 503},
            ResponseStatus(response_action=ResponseAction.FAIL, error_message="custom error message"),
            id="test_http_code_matches",
        ),
        pytest.param(
            ResponseAction.IGNORE,
            {403},
            "",
            "",
            None,
            "",
            {"status_code": 403},
            ResponseStatus(response_action=ResponseAction.IGNORE),
            id="test_http_code_matches_ignore_action",
        ),
        pytest.param(
            ResponseAction.RETRY,
            {429},
            "",
            "",
            30,
            "",
            {"status_code": 429},
            ResponseStatus(response_action=ResponseAction.RETRY, retry_in=30),
            id="test_http_code_matches_retry_action",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {},
            '{{ response.the_body == "do_i_match" }}',
            "",
            None,
            "error message was: {{ response.failure }}",
            {"status_code": 404, "json": {"the_body": "do_i_match", "failure": "i failed you"}},
            ResponseStatus(response_action=ResponseAction.FAIL, error_message="error message was: i failed you"),
            id="test_predicate_matches_json",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {},
            '{{ headers.the_key == "header_match" }}',
            "",
            None,
            "error from header: {{ headers.warning }}",
            {"status_code": 404, "headers": {"the_key": "header_match", "warning": "this failed"}},
            ResponseStatus(response_action=ResponseAction.FAIL, error_message="error from header: this failed"),
            id="test_predicate_matches_headers",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {},
            None,
            "DENIED",
            None,
            "",
            {"status_code": 403, "json": {"error": "REQUEST_DENIED"}},
            ResponseStatus(response_action=ResponseAction.FAIL),
            id="test_predicate_matches_headers",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {400, 404},
            '{{ headers.error == "invalid_input" or response.reason == "bad request"}}',
            "",
            None,
            "",
            {"status_code": 403, "headers": {"error": "authentication_error"}, "json": {"reason": "permission denied"}},
            None,
            id="test_response_does_not_match_filter",
        ),
    ],
)
def test_matches(requests_mock, action, http_codes, predicate, error_contains, back_off, error_message, response, expected_response_status):
    requests_mock.register_uri(
        "GET",
        "https://airbyte.io/",
        text=response.get("json") and json.dumps(response.get("json")),
        headers=response.get("headers") or {},
        status_code=response.get("status_code"),
    )
    response = requests.get("https://airbyte.io/")
    response_filter = HttpResponseFilter(
        action=action,
        config={},
        parameters={},
        http_codes=http_codes,
        predicate=predicate,
        error_message_contains=error_contains,
        error_message=error_message,
    )

    actual_response_status = response_filter.matches(response, backoff_time=back_off or 10)
    if expected_response_status:
        assert actual_response_status.action == expected_response_status.action
        assert actual_response_status.retry_in == expected_response_status.retry_in
        assert actual_response_status.error_message == expected_response_status.error_message
    else:
        assert actual_response_status is None
