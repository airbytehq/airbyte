#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction


@pytest.fixture
def manifest() -> dict:
    with (Path(__file__).parent.parent / "manifest.yaml").open() as manifest_file:
        return yaml.safe_load(manifest_file)


def create_handler(manifest: dict, config: dict, definition: str):
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    handler = resolved["definitions"][definition]
    if definition == "analytics_retriever":
        handler = handler["requester"]["error_handler"]
    return ModelToComponentFactory().create_component(getattr(models, handler["type"]), handler, config)


def response(status: int, body: dict, headers: dict | None = None) -> requests.Response:
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(body).encode()
    result.headers.update(headers or {})
    result.request = requests.Request("GET", "https://api.pinterest.com/v5/user_account/analytics").prepare()
    return result


@pytest.fixture
def analytics_handler(manifest: dict, test_config: dict):
    return create_handler(manifest, test_config, "analytics_retriever")


def test_analytics_uses_single_handler(analytics_handler, manifest: dict) -> None:
    assert type(analytics_handler) is DefaultErrorHandler
    assert len(manifest["definitions"]["analytics_retriever"]["requester"]["error_handler"]["response_filters"]) == 4
    assert analytics_handler.backoff_strategies
    assert len(analytics_handler.backoff_strategies) == 1
    assert analytics_handler.max_retries == 5
    assert analytics_handler.max_time == 600


@pytest.mark.parametrize("body", [{}, {"code": 1}, {"code": 8}, {"code": 12}, {"message": "Retry after 5 seconds"}])
def test_analytics_retries_every_400(analytics_handler, body: dict) -> None:
    resolution = analytics_handler.interpret_response(response(400, body))
    assert resolution.response_action is ResponseAction.RETRY
    assert resolution.failure_type is FailureType.system_error
    assert resolution.error_message == "HTTP Status Code: 400. Error: Bad request. Please check your request parameters."


@pytest.mark.parametrize(
    "status,body,action,failure_type,message",
    [
        (200, {"code": 8}, ResponseAction.SUCCESS, None, None),
        (200, {"message": "Retry after 5 seconds"}, ResponseAction.RETRY, FailureType.system_error, ""),
        (200, {"code": 12}, ResponseAction.RETRY, FailureType.system_error, "Pinterest API request failed due to a temporary error."),
        (429, {"code": 8}, ResponseAction.RATE_LIMITED, FailureType.transient_error, "Rate limit exceeded for Pinterest API."),
        (429, {}, ResponseAction.RATE_LIMITED, FailureType.transient_error, "HTTP Status Code: 429. Error: Too many requests."),
        (401, {}, ResponseAction.FAIL, FailureType.config_error, "Try to re-authenticate because current refresh token is not valid."),
        (
            403,
            {},
            ResponseAction.FAIL,
            FailureType.config_error,
            "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource.",
        ),
        (
            404,
            {},
            ResponseAction.FAIL,
            FailureType.system_error,
            "HTTP Status Code: 404. Error: Not found. The requested resource was not found on the server.",
        ),
        (500, {}, ResponseAction.RETRY, FailureType.transient_error, "HTTP Status Code: 500. Error: Internal server error."),
        (503, {}, ResponseAction.RETRY, FailureType.transient_error, "HTTP Status Code: 503. Error: Service unavailable."),
    ],
)
def test_analytics_resolutions(
    analytics_handler, status: int, body: dict, action: ResponseAction, failure_type: FailureType | None, message: str | None
) -> None:
    assert analytics_handler.interpret_response(response(status, body)) == ErrorResolution(action, failure_type, message)


@pytest.mark.parametrize("body", [{}, {"code": 8}])
def test_analytics_does_not_ignore_409(analytics_handler, body: dict) -> None:
    assert analytics_handler.interpret_response(response(409, body)).response_action is ResponseAction.RETRY


@pytest.mark.parametrize("status", [200, 400, 401, 403, 404, 408, 409, 429, 500, 503])
@pytest.mark.parametrize("body,expected", [({"message": "Retry after 17 seconds"}, 17.0), ({}, 8)])
def test_analytics_backoff(analytics_handler, status: int, body: dict, expected: float) -> None:
    assert (
        analytics_handler.backoff_strategies[0].backoff_time(response(status, body, {"X-RateLimit-Reset": "999"}), attempt_count=3)
        == expected
    )


@pytest.mark.parametrize("status", [401, 403, 404, 405])
def test_body_rate_limit_code_does_not_override_http_failure(analytics_handler, status: int) -> None:
    assert analytics_handler.interpret_response(response(status, {"code": 8})).response_action is ResponseAction.FAIL


@pytest.mark.parametrize("definition", ["base_error_handler", "analytics_error_handler"])
def test_standalone_handlers(manifest: dict, test_config: dict, definition: str) -> None:
    handler = create_handler(manifest, test_config, definition)
    resolution = handler.interpret_response(response(200, {"code": 8}))
    assert resolution.response_action is (ResponseAction.RATE_LIMITED if definition == "base_error_handler" else ResponseAction.SUCCESS)
    assert handler.interpret_response(response(409, {})).response_action is (
        ResponseAction.IGNORE if definition == "base_error_handler" else ResponseAction.RETRY
    )
