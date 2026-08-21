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
    "status_code, response_json, expected_action, expected_failure_type",
    [
        pytest.param(
            429,
            _graphql_error("RATELIMITED"),
            ResponseAction.RATE_LIMITED,
            FailureType.transient_error,
            id="rate_limited",
        ),
        pytest.param(
            401,
            _graphql_error(
                "AUTHENTICATION_ERROR",
                user_message="You need to authenticate to access this operation.",
            ),
            ResponseAction.FAIL,
            FailureType.config_error,
            id="authentication_error",
        ),
        pytest.param(
            403,
            _graphql_error("FORBIDDEN", user_message="You do not have access to this data."),
            ResponseAction.FAIL,
            FailureType.config_error,
            id="forbidden",
        ),
        pytest.param(
            400,
            _graphql_error("FEATURE_NOT_ACCESSIBLE", user_message="Customer Requests is not enabled."),
            ResponseAction.FAIL,
            FailureType.config_error,
            id="feature_not_accessible",
        ),
        pytest.param(
            400,
            _graphql_error("GRAPHQL_VALIDATION_FAILED", message="Cannot query field 'deprecatedField'."),
            ResponseAction.FAIL,
            FailureType.system_error,
            id="graphql_validation_failed_bad_request",
        ),
        pytest.param(
            500,
            _graphql_error("GRAPHQL_VALIDATION_FAILED", message="Syntax Error: Unexpected Name."),
            ResponseAction.FAIL,
            FailureType.system_error,
            id="graphql_validation_failed_server_error",
        ),
        pytest.param(
            200,
            _graphql_error("UNKNOWN_ERROR", user_message="Something went wrong."),
            ResponseAction.FAIL,
            FailureType.system_error,
            id="generic_graphql_error",
        ),
        pytest.param(
            200,
            {"data": {"issues": {"nodes": []}}},
            ResponseAction.SUCCESS,
            None,
            id="clean_success",
        ),
    ],
)
def test_graphql_error_classification(
    error_handler: Any,
    status_code: int,
    response_json: Mapping[str, Any],
    expected_action: ResponseAction,
    expected_failure_type: FailureType | None,
) -> None:
    response = MagicMock(spec=Response, status_code=status_code)
    response.ok = status_code == 200
    response.headers = {"Content-Type": "application/json", "X-RateLimit-Requests-Reset": "1600000060000"}
    response.json.return_value = response_json

    result = error_handler.interpret_response(response)

    assert result.response_action == expected_action
    assert result.failure_type == expected_failure_type

    if response_json.get("errors", [{}])[0].get("extensions", {}).get("code") == "AUTHENTICATION_ERROR":
        assert "You need to authenticate to access this operation." in result.error_message
