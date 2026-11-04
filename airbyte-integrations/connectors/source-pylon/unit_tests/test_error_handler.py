# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

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
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.utils import AirbyteTracedException


@pytest.fixture
def error_handler(manifest_path: Path) -> DefaultErrorHandler:
    manifest = yaml.safe_load(manifest_path.read_text())
    definition = manifest["definitions"]["error_handler"]
    return ModelToComponentFactory().create_component(
        model_type=getattr(models, definition["type"]), component_definition=definition, config={}
    )


def test_streams_use_the_shared_default_error_handler(manifest_path: Path) -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    for stream in manifest["streams"]:
        requester = stream["retriever"]["requester"]
        assert requester["error_handler"] == manifest["definitions"]["error_handler"], stream["name"]
        assert requester["connect_timeout_in_seconds"] == 30
        assert requester["read_timeout_in_seconds"] == 300


@pytest.mark.parametrize(
    ("status_code", "expected_action"),
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
        (504, ResponseAction.RETRY),
    ],
)
def test_response_classification(error_handler, status_code: int, expected_action: ResponseAction) -> None:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"

    resolution = error_handler.interpret_response(response)

    assert resolution.response_action == expected_action
    if status_code in (401, 403):
        assert resolution.failure_type == FailureType.config_error
    if status_code in (429, 500, 502, 503, 504):
        assert resolution.failure_type == FailureType.transient_error


def test_retry_after_precedes_exponential_backoff(error_handler) -> None:
    assert error_handler.max_retries == 5
    assert len(error_handler.backoff_strategies) == 2
    header, exponential = error_handler.backoff_strategies
    response = requests.Response()
    response.status_code = 429
    response.headers["Retry-After"] = "7"
    assert header.backoff_time(response, attempt_count=0) == 7
    assert error_handler.backoff_time(response, attempt_count=0) == 7
    response.headers.clear()
    assert header.backoff_time(response, attempt_count=0) is None
    assert [exponential.backoff_time(response, attempt_count=attempt) for attempt in range(3)] == [5, 10, 20]
    assert [error_handler.backoff_time(response, attempt_count=attempt) for attempt in range(3)] == [5, 10, 20]


@pytest.mark.parametrize("status", [400, 401, 403])
@pytest.mark.parametrize(
    "code,expected_text",
    [
        ("wrong_region_token", "EU tokens starting with pylon_api_eu_ are not supported"),
        ("invalid_api_token", "IP allowlist"),
        ("invalid_authorization_header", "without a 'Bearer ' prefix or spaces"),
        ("organization_deactivated", "Contact Pylon support"),
        ("organization_suspended", "Contact Pylon support"),
    ],
)
def test_code_filters_precede_generic_status_filters(
    error_handler: DefaultErrorHandler, status: int, code: str, expected_text: str
) -> None:
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps({"code": code}).encode()
    resolution = error_handler.interpret_response(response)
    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert expected_text in resolution.error_message


def test_permission_error_includes_endpoint_without_query_or_credentials(error_handler: DefaultErrorHandler) -> None:
    response = requests.Response()
    response.status_code = 403
    response._content = b"{}"
    response.url = "https://synthetic:password@api.usepylon.com/tags?token=synthetic-secret#fragment"
    message = error_handler.interpret_response(response).error_message
    assert "https://api.usepylon.com/tags" in message
    assert "Give the token's role access" in message
    assert "synthetic" not in message
    assert "password" not in message


@pytest.mark.parametrize("body", [b"{}", b"not-json"])
def test_generic_unauthorized_error_handles_missing_codes(error_handler: DefaultErrorHandler, body: bytes) -> None:
    response = requests.Response()
    response.status_code = 401
    response._content = body
    resolution = error_handler.interpret_response(response)
    assert resolution.failure_type == FailureType.config_error
    assert "update the token in your Airbyte source settings" in resolution.error_message


@pytest.mark.parametrize("header_value", ["120", "121"])
def test_excessive_retry_after_stops_instead_of_waiting(error_handler: DefaultErrorHandler, header_value: str) -> None:
    response = requests.Response()
    response.status_code = 429
    response.headers["Retry-After"] = header_value
    with pytest.raises(AirbyteTracedException) as exc:
        error_handler.backoff_time(response, attempt_count=0)
    assert exc.value.failure_type == FailureType.transient_error
