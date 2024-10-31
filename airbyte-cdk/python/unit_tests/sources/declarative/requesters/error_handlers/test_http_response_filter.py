#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers import HttpResponseFilter
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction


@pytest.mark.parametrize(
    "action, failure_type, http_codes, predicate, error_contains, error_message, response, expected_error_resolution",
    [
        pytest.param(
            ResponseAction.FAIL,
            None,
            {501, 503},
            "",
            "",
            "custom error message",
            {"status_code": 503},
            ErrorResolution(
                response_action=ResponseAction.FAIL, failure_type=FailureType.transient_error, error_message="custom error message"
            ),
            id="test_http_code_matches",
        ),
        pytest.param(
            ResponseAction.IGNORE,
            None,
            {403},
            "",
            "",
            "",
            {"status_code": 403},
            ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Forbidden. You don't have permission to access this resource.",
            ),
            id="test_http_code_matches_ignore_action",
        ),
        pytest.param(
            ResponseAction.RETRY,
            None,
            {429},
            "",
            "",
            "",
            {"status_code": 429},
            ErrorResolution(
                response_action=ResponseAction.RETRY, failure_type=FailureType.transient_error, error_message="Too many requests."
            ),
            id="test_http_code_matches_retry_action",
        ),
        pytest.param(
            ResponseAction.FAIL,
            None,
            {},
            '{{ response.the_body == "do_i_match" }}',
            "",
            "error message was: {{ response.failure }}",
            {"status_code": 404, "json": {"the_body": "do_i_match", "failure": "i failed you"}},
            ErrorResolution(
                response_action=ResponseAction.FAIL, failure_type=FailureType.system_error, error_message="error message was: i failed you"
            ),
            id="test_predicate_matches_json",
        ),
        pytest.param(
            ResponseAction.FAIL,
            None,
            {},
            '{{ headers.the_key == "header_match" }}',
            "",
            "error from header: {{ headers.warning }}",
            {"status_code": 404, "headers": {"the_key": "header_match", "warning": "this failed"}},
            ErrorResolution(
                response_action=ResponseAction.FAIL, failure_type=FailureType.system_error, error_message="error from header: this failed"
            ),
            id="test_predicate_matches_headers",
        ),
        pytest.param(
            ResponseAction.FAIL,
            None,
            {},
            None,
            "DENIED",
            "",
            {"status_code": 403, "json": {"error": "REQUEST_DENIED"}},
            ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.config_error,
                error_message="Forbidden. You don't have permission to access this resource.",
            ),
            id="test_predicate_matches_headers",
        ),
        pytest.param(
            ResponseAction.FAIL,
            None,
            {400, 404},
            '{{ headers.error == "invalid_input" or response.reason == "bad request"}}',
            "",
            "",
            {"status_code": 403, "headers": {"error": "authentication_error"}, "json": {"reason": "permission denied"}},
            None,
            id="test_response_does_not_match_filter",
        ),
        pytest.param(
            ResponseAction.FAIL,
            FailureType.config_error,
            {403, 404},
            "",
            "",
            "check permissions",
            {"status_code": 403},
            ErrorResolution(response_action=ResponseAction.FAIL, failure_type=FailureType.config_error, error_message="check permissions"),
            id="test_http_code_matches_failure_type_config_error",
        ),
        pytest.param(
            ResponseAction.FAIL,
            FailureType.system_error,
            {403, 404},
            "",
            "",
            "check permissions",
            {"status_code": 403},
            ErrorResolution(response_action=ResponseAction.FAIL, failure_type=FailureType.system_error, error_message="check permissions"),
            id="test_http_code_matches_failure_type_system_error",
        ),
        pytest.param(
            ResponseAction.FAIL,
            FailureType.transient_error,
            {500},
            "",
            "",
            "rate limits",
            {"status_code": 500},
            ErrorResolution(response_action=ResponseAction.FAIL, failure_type=FailureType.transient_error, error_message="rate limits"),
            id="test_http_code_matches_failure_type_transient_error",
        ),
        pytest.param(
            ResponseAction.RETRY,
            FailureType.config_error,
            {500},
            "",
            "",
            "rate limits",
            {"status_code": 500},
            ErrorResolution(response_action=ResponseAction.RETRY, failure_type=FailureType.transient_error, error_message="rate limits"),
            id="test_http_code_matches_failure_type_config_error_action_retry_uses_default_failure_type",
        ),
        pytest.param(
            ResponseAction.RATE_LIMITED,
            None,
            {500},
            "",
            "",
            "rate limits",
            {"status_code": 500},
            ErrorResolution(
                response_action=ResponseAction.RATE_LIMITED, failure_type=FailureType.transient_error, error_message="rate limits"
            ),
            id="test_http_code_matches_response_action_rate_limited",
        ),
    ],
)
def test_matches(
    requests_mock, action, failure_type, http_codes, predicate, error_contains, error_message, response, expected_error_resolution
):
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
        failure_type=failure_type,
        config={},
        parameters={},
        http_codes=http_codes,
        predicate=predicate,
        error_message_contains=error_contains,
        error_message=error_message,
    )

    actual_response_status = response_filter.matches(response)
    if expected_error_resolution:
        assert actual_response_status.response_action == expected_error_resolution.response_action
        assert actual_response_status.failure_type == expected_error_resolution.failure_type
        assert actual_response_status.error_message == expected_error_resolution.error_message
    else:
        assert actual_response_status is None
