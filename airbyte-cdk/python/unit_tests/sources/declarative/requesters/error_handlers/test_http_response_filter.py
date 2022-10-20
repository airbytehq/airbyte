#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction


@pytest.mark.parametrize(
    "action, http_codes, predicate, error_contains, response, expected_response_action",
    [
        pytest.param(ResponseAction.FAIL, {501, 503}, "", "", {"status_code": 503}, ResponseAction.FAIL, id="test_http_code_matches"),
        pytest.param(
            ResponseAction.IGNORE, {403}, "", "", {"status_code": 403}, ResponseAction.IGNORE, id="test_http_code_matches_ignore_action"
        ),
        pytest.param(
            ResponseAction.FAIL,
            {},
            '{{ response.the_body == "do_i_match" }}',
            "",
            {"status_code": 404, "json": {"the_body": "do_i_match"}},
            ResponseAction.FAIL,
            id="test_predicate_matches_json",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {},
            '{{ headers.the_key == "header_match" }}',
            "",
            {"status_code": 404, "headers": {"the_key": "header_match"}},
            ResponseAction.FAIL,
            id="test_predicate_matches_headers",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {},
            None,
            "DENIED",
            {"status_code": 403, "json": {"error": "REQUEST_DENIED"}},
            ResponseAction.FAIL,
            id="test_predicate_matches_headers",
        ),
        pytest.param(
            ResponseAction.FAIL,
            {400, 404},
            '{{ headers.error == "invalid_input" or response.reason == "bad request"}}',
            "",
            {"status_code": 403, "headers": {"error", "authentication_error"}, "json": {"reason": "permission denied"}},
            None,
            id="test_response_does_not_match_filter",
        ),
    ],
)
def test_matches(action, http_codes, predicate, error_contains, response, expected_response_action):
    mock_response = MagicMock()
    mock_response.status_code = response.get("status_code")
    mock_response.headers = response.get("headers")
    mock_response.json.return_value = response.get("json")

    response_filter = HttpResponseFilter(
        action=action, config={}, options={}, http_codes=http_codes, predicate=predicate, error_message_contains=error_contains
    )
    actual_response_action = response_filter.matches(mock_response)
    assert actual_response_action == expected_response_action


@pytest.mark.parametrize(
    "error_message_template, response_json, response_headers, expected_error_message",
    [
        pytest.param("", None, None, "", id="test_create_error_message"),
        pytest.param(
            "Error using {{ response.key }} from response body",
            {"key": "some_value"},
            None,
            "Error using some_value from response body",
            id="test_create_error_message_with_json_interpolation",
        ),
        pytest.param(
            "Error using {{ headers.from }} from response headers",
            None,
            {"from": "head_value"},
            "Error using head_value from response headers",
            id="test_create_error_message_with_header_interpolation",
        ),
        pytest.param(None, None, None, "", id="test_no_error_message_returns_empty_string"),
    ],
)
def test_create_error_message(error_message_template, response_json, response_headers, expected_error_message):
    response = MagicMock()
    response.json.return_value = response_json
    response.headers = response_headers

    response_filter = HttpResponseFilter(action=ResponseAction.FAIL, config={}, options={}, error_message=error_message_template)
    actual_error_message = response_filter.create_error_message(response=response)
    assert actual_error_message == expected_error_message
