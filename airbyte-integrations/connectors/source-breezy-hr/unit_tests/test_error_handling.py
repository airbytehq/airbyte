# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import cast

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import CompositeErrorHandler as CompositeErrorHandlerModel
from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers import CompositeErrorHandler, DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


CONFIG = {"api_key": "test-api-key", "company_id": "test-company"}
AUTH_MESSAGE = (
    "Breezy HR access token is missing or invalid. Set API Key to a valid Personal Access Token from Breezy HR's My Settings > API Keys."
)
ACCESS_MESSAGE = (
    "Breezy HR denied access to the configured company. Verify Company ID is the company's _id and the API Key's user has access to that company."
)
RATE_LIMIT_MESSAGE = "Breezy HR API rate limit exceeded for the candidates stream."


@pytest.fixture(scope="module", params=["positions", "candidates", "pipelines"])
def error_handler(request: pytest.FixtureRequest) -> DefaultErrorHandler | CompositeErrorHandler:
    manifest_path = Path(__file__).resolve().parents[1] / "manifest.yaml"
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    definition = manifest["definitions"]["streams"][request.param]["retriever"]["requester"]["error_handler"]
    model = CompositeErrorHandlerModel if definition["type"] == "CompositeErrorHandler" else DefaultErrorHandlerModel
    return cast(
        DefaultErrorHandler | CompositeErrorHandler,
        ModelToComponentFactory().create_component(model, definition, CONFIG),
    )


def response(status_code: int, body: object, headers: dict[str, str] | None = None) -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result._content = json.dumps(body).encode()
    result.headers.update(headers or {})
    return result


@pytest.mark.parametrize(
    "status_code,body,failure_type,message",
    [
        (400, {"error": {"type": "missingAccessToken"}}, FailureType.config_error, AUTH_MESSAGE),
        (400, {"error": {"type": "invalidAccessToken"}}, FailureType.config_error, AUTH_MESSAGE),
        (401, {"error": {"type": "invalidAccessToken"}}, FailureType.config_error, AUTH_MESSAGE),
        (401, {}, FailureType.config_error, AUTH_MESSAGE),
        (400, {"error": {"type": "invalidParameter"}}, FailureType.system_error, "Breezy HR rejected the API request as invalid."),
        (400, {}, FailureType.system_error, "Breezy HR rejected the API request as invalid."),
        (403, {"error": {"type": "companyMembershipRequired"}}, FailureType.config_error, ACCESS_MESSAGE),
        (403, {}, FailureType.config_error, ACCESS_MESSAGE),
    ],
)
def test_error_classification(
    error_handler: DefaultErrorHandler | CompositeErrorHandler,
    status_code: int,
    body: dict,
    failure_type: FailureType,
    message: str,
) -> None:
    body.setdefault("error", {})["message"] = "Sensitive upstream detail: test-company test-api-key https://example.com"
    result = error_handler.interpret_response(response(status_code, body))

    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == failure_type
    assert result.error_message == message


@pytest.mark.parametrize("body", [None, [], "invalid token", {"error": None}, {"error": "invalid token"}])
@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_unexpected_error_body(
    error_handler: DefaultErrorHandler | CompositeErrorHandler, status_code: int, body: object
) -> None:
    result = error_handler.interpret_response(response(status_code, body))

    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == (FailureType.system_error if status_code == 400 else FailureType.config_error)
    assert result.error_message
    assert "{{" not in result.error_message


def test_candidates_rate_limit(error_handler: DefaultErrorHandler | CompositeErrorHandler) -> None:
    result = error_handler.interpret_response(response(429, {"error": {"message": "Rate limit exceeded"}}))

    assert result.failure_type == FailureType.transient_error
    if isinstance(error_handler, CompositeErrorHandler):
        assert result.response_action == ResponseAction.RETRY
        assert result.error_message == RATE_LIMIT_MESSAGE
        assert error_handler.max_retries == 100
    else:
        assert result.response_action == ResponseAction.RATE_LIMITED


@pytest.mark.parametrize("retry_after", ["1", "45", "120"])
def test_retry_after_precedes_other_backoffs(
    error_handler: DefaultErrorHandler | CompositeErrorHandler, retry_after: str
) -> None:
    result = response(429, {}, {"Retry-After": retry_after, "X-RateLimit-Reset": "9999999999"})
    assert error_handler.backoff_strategies

    for strategy in error_handler.backoff_strategies:
        delay = strategy.backoff_time(result, attempt_count=0)
        if delay is not None:
            break

    assert delay == float(retry_after)


@pytest.mark.parametrize("headers", [{}, {"Retry-After": "invalid"}])
def test_candidates_preserves_five_second_fallback(
    error_handler: DefaultErrorHandler | CompositeErrorHandler, headers: dict[str, str]
) -> None:
    if not isinstance(error_handler, CompositeErrorHandler):
        return

    for strategy in error_handler.backoff_strategies:
        delay = strategy.backoff_time(response(429, {}, headers), attempt_count=0)
        if delay is not None:
            break

    assert delay == 5


@pytest.mark.parametrize("status_code,action", [(200, ResponseAction.SUCCESS), (500, ResponseAction.RETRY)])
def test_other_responses_preserve_default_behavior(
    error_handler: DefaultErrorHandler | CompositeErrorHandler, status_code: int, action: ResponseAction
) -> None:
    assert error_handler.interpret_response(response(status_code, {})).response_action == action
