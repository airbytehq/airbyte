# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for Linear GraphQL error classification."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from requests import Response

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
CONFIG: Mapping[str, Any] = {
    "api_key": "test-api-key",
    "start_date": "2024-01-01T00:00:00.000Z",
}


@pytest.fixture(scope="module")
def error_handler() -> Any:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams_by_name = {stream.name: stream for stream in source.streams(config=CONFIG)}
    stream = streams_by_name["issues"]
    return next(iter(stream.generate_partitions()))._retriever.requester.error_handler


def _graphql_error(code: str, *, message: str = "GraphQL error.", user_message: str | None = None) -> Mapping[str, Any]:
    extensions: dict[str, str] = {"code": code}
    if user_message:
        extensions["userPresentableMessage"] = user_message
    return {"errors": [{"message": message, "extensions": extensions}]}


@pytest.mark.parametrize(
    "status_code, response_json, expected_action, expected_failure_type, expected_error_message",
    [
        pytest.param(
            429,
            _graphql_error("RATELIMITED"),
            ResponseAction.RATE_LIMITED,
            FailureType.transient_error,
            "Rate limit exceeded for Linear API.",
            id="rate_limited",
        ),
        pytest.param(
            429,
            _graphql_error("UNKNOWN_ERROR"),
            ResponseAction.RATE_LIMITED,
            FailureType.transient_error,
            "Rate limit exceeded for Linear API.",
            id="http_rate_limited",
        ),
        pytest.param(
            500,
            _graphql_error("UNKNOWN_ERROR"),
            ResponseAction.RETRY,
            FailureType.transient_error,
            "Linear returned a transient error; retrying.",
            id="http_server_error",
        ),
        pytest.param(
            401,
            _graphql_error(
                "AUTHENTICATION_ERROR",
                user_message="You need to authenticate to access this operation.",
            ),
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear rejected the credentials. "
            "If you authenticated with an API key, confirm it has not been revoked in Linear under "
            "Settings → Security & access → Personal API keys. "
            "If you authenticated with OAuth, re-authenticate to obtain a new refresh token. "
            "Linear's message: You need to authenticate to access this operation.",
            id="authentication_error",
        ),
        pytest.param(
            403,
            _graphql_error("FORBIDDEN", user_message="You do not have access to this data."),
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear denied access to this data. "
            "Confirm the credentials you configured can read the teams and data this stream covers. If the failing stream is "
            "customers, customer_needs, customer_statuses or customer_tiers, your workspace also needs Linear's Customer "
            "Requests feature enabled (Workspace Settings > Customer requests) and, for OAuth sources, the customer:read "
            "scope. Deselect the stream if you cannot grant it access. "
            "Linear's message: You do not have access to this data.",
            id="forbidden",
        ),
        pytest.param(
            400,
            _graphql_error("FEATURE_NOT_ACCESSIBLE", user_message="Customer Requests is not enabled."),
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear denied access to this data. "
            "Confirm the credentials you configured can read the teams and data this stream covers. If the failing stream is "
            "customers, customer_needs, customer_statuses or customer_tiers, your workspace also needs Linear's Customer "
            "Requests feature enabled (Workspace Settings > Customer requests) and, for OAuth sources, the customer:read "
            "scope. Deselect the stream if you cannot grant it access. "
            "Linear's message: Customer Requests is not enabled.",
            id="feature_not_accessible",
        ),
        pytest.param(
            400,
            _graphql_error("GRAPHQL_VALIDATION_FAILED", message="Cannot query field 'deprecatedField'."),
            ResponseAction.FAIL,
            FailureType.system_error,
            "Linear rejected the connector's query as invalid. "
            "This is a connector defect, not a configuration problem. Please report it to Airbyte support. "
            "Linear's message: Cannot query field 'deprecatedField'.",
            id="graphql_validation_failed_bad_request",
        ),
        pytest.param(
            500,
            _graphql_error("GRAPHQL_VALIDATION_FAILED", message="Syntax Error: Unexpected Name."),
            ResponseAction.FAIL,
            FailureType.system_error,
            "Linear rejected the connector's query as invalid. "
            "This is a connector defect, not a configuration problem. Please report it to Airbyte support. "
            "Linear's message: Syntax Error: Unexpected Name.",
            id="graphql_validation_failed_server_error",
        ),
        pytest.param(
            200,
            _graphql_error("UNKNOWN_ERROR", user_message="Something went wrong."),
            ResponseAction.FAIL,
            FailureType.system_error,
            "Linear returned an error: Something went wrong.",
            id="generic_graphql_error",
        ),
        pytest.param(
            200,
            {"errors": [{"message": "GraphQL error without extensions."}]},
            ResponseAction.FAIL,
            FailureType.system_error,
            "Linear returned an error: GraphQL error without extensions.",
            id="graphql_error_without_extensions",
        ),
        pytest.param(
            200,
            {"data": {"issues": {"nodes": []}}},
            ResponseAction.SUCCESS,
            None,
            None,
            id="clean_success",
        ),
        pytest.param(
            200,
            {
                "data": {"issues": {"nodes": [{"id": "i1", "updatedAt": "2024-06-01T00:00:00.000Z"}]}},
                "errors": [{"message": "Access denied.", "extensions": {"code": "FORBIDDEN"}}],
            },
            ResponseAction.SUCCESS,
            None,
            None,
            id="partial_success_keeps_records",
        ),
        pytest.param(
            200,
            {"data": {"issues": None}, "errors": [{"message": "Access denied.", "extensions": {"code": "FORBIDDEN"}}]},
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear denied access to this data. "
            "Confirm the credentials you configured can read the teams and data this stream covers. If the failing stream is "
            "customers, customer_needs, customer_statuses or customer_tiers, your workspace also needs Linear's Customer "
            "Requests feature enabled (Workspace Settings > Customer requests) and, for OAuth sources, the customer:read "
            "scope. Deselect the stream if you cannot grant it access. Linear's message: access denied",
            id="null_top_level_field_still_fails",
        ),
        pytest.param(
            403,
            {
                "errors": [
                    {
                        "message": "You do not have access to this data.",
                        "extensions": {"type": "forbidden", "userPresentableMessage": "You do not have access to this data."},
                    }
                ]
            },
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear denied access to this data. "
            "Confirm the credentials you configured can read the teams and data this stream covers. If the failing stream is "
            "customers, customer_needs, customer_statuses or customer_tiers, your workspace also needs Linear's Customer "
            "Requests feature enabled (Workspace Settings > Customer requests) and, for OAuth sources, the customer:read "
            "scope. Deselect the stream if you cannot grant it access. "
            "Linear's message: You do not have access to this data.",
            id="forbidden_type_only",
        ),
        pytest.param(
            401,
            {"errors": [{"extensions": {"code": "AUTHENTICATION_ERROR"}}]},
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear rejected the credentials. "
            "If you authenticated with an API key, confirm it has not been revoked in Linear under "
            "Settings → Security & access → Personal API keys. "
            "If you authenticated with OAuth, re-authenticate to obtain a new refresh token. "
            "Linear's message: authentication failed",
            id="authentication_error_without_user_message",
        ),
        pytest.param(
            403,
            {"errors": [{"extensions": {"code": "FORBIDDEN"}}]},
            ResponseAction.FAIL,
            FailureType.config_error,
            "Linear denied access to this data. "
            "Confirm the credentials you configured can read the teams and data this stream covers. If the failing stream is "
            "customers, customer_needs, customer_statuses or customer_tiers, your workspace also needs Linear's Customer "
            "Requests feature enabled (Workspace Settings > Customer requests) and, for OAuth sources, the customer:read "
            "scope. Deselect the stream if you cannot grant it access. Linear's message: access denied",
            id="forbidden_without_user_message",
        ),
        pytest.param(
            200,
            {"errors": ["Request blocked"]},
            ResponseAction.FAIL,
            FailureType.system_error,
            "Linear returned an error: Request blocked",
            id="malformed_error_string",
        ),
        pytest.param(
            200,
            {"errors": [{"message": "x", "extensions": None}]},
            ResponseAction.FAIL,
            FailureType.system_error,
            "Linear returned an error: x",
            id="malformed_extensions_null",
        ),
    ],
)
def test_graphql_error_classification(
    error_handler: Any,
    status_code: int,
    response_json: Mapping[str, Any],
    expected_action: ResponseAction,
    expected_failure_type: FailureType | None,
    expected_error_message: str | None,
) -> None:
    response = MagicMock(spec=Response, status_code=status_code)
    response.ok = status_code == 200
    response.headers = {"Content-Type": "application/json", "X-RateLimit-Requests-Reset": "1600000060000"}
    response.json.return_value = response_json

    result = error_handler.interpret_response(response)

    assert result.response_action == expected_action
    assert result.failure_type == expected_failure_type
    assert result.error_message == expected_error_message
