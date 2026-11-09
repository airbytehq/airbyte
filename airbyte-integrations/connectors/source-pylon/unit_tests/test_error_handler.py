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


@pytest.fixture(scope="module")
def error_handler(manifest_path: Path) -> DefaultErrorHandler:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    definition = manifest["definitions"]["error_handler"]
    return ModelToComponentFactory().create_component(
        model_type=getattr(models, definition["type"]), component_definition=definition, config={}
    )


@pytest.fixture(scope="module")
def thread_error_handler(manifest_path: Path) -> DefaultErrorHandler:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    definition = manifest["definitions"]["issue_threads_error_handler"]
    return ModelToComponentFactory().create_component(model_type=models.DefaultErrorHandler, component_definition=definition, config={})


def test_streams_use_the_shared_default_error_handler(manifest_path: Path) -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    for stream in manifest["streams"]:
        requester = stream["retriever"]["requester"]
        if stream["name"] == "issue_threads":
            assert requester["error_handler"] == manifest["definitions"]["issue_threads_error_handler"]
            shared = manifest["definitions"]["error_handler"]
            threads = requester["error_handler"]
            assert threads["response_filters"][:-2] == shared["response_filters"]
            assert {key: value for key, value in threads.items() if key != "response_filters"} == {
                key: value for key, value in shared.items() if key != "response_filters"
            }
        else:
            assert requester["error_handler"] == manifest["definitions"]["error_handler"], stream["name"]
        assert requester["connect_timeout_in_seconds"] == 30
        assert requester["read_timeout_in_seconds"] == 300


def test_coded_statuses_outside_equality_matrix(error_handler, thread_error_handler) -> None:
    differing_statuses = []
    for status in range(400, 600):
        response = requests.Response()
        response.status_code = status
        response._content = b'{"code": "synthetic_error"}'
        shared = error_handler.interpret_response(response)
        threads = thread_error_handler.interpret_response(response)
        if shared.response_action == ResponseAction.RETRY and threads.response_action == ResponseAction.FAIL:
            differing_statuses.append(status)
    assert differing_statuses == [402, *range(406, 429), *range(430, 500), 501, *range(505, 600)]


@pytest.mark.parametrize("status", [200, 201, 204, 206])
def test_coded_success_without_data_differs_from_shared(error_handler, thread_error_handler, status: int) -> None:
    response = requests.Response()
    response.status_code = status
    response._content = b'{"code": "synthetic_error"}'
    assert error_handler.interpret_response(response).response_action == ResponseAction.SUCCESS
    assert thread_error_handler.interpret_response(response).response_action == ResponseAction.FAIL


def test_manifest_has_no_composite_error_handlers(manifest_path: Path) -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))

    def check(node: object) -> None:
        if isinstance(node, dict):
            assert node.get("type") != "CompositeErrorHandler"
            for value in node.values():
                check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)

    check(manifest)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500, 502, 503, 504])
@pytest.mark.parametrize(
    "body",
    [
        {},
        {"code": None},
        {"code": "wrong_region_token"},
        {"code": "invalid_api_token"},
        {"code": "invalid_authorization_header"},
        {"code": "organization_deactivated"},
        {"code": "organization_suspended"},
        {"code": "rate_limited"},
        {"code": "not_found"},
        {"code": "synthetic_error"},
    ],
)
@pytest.mark.parametrize("headers", [{}, {"Retry-After": "7"}, {"X-Retry-After": "13"}, {"Retry-After": "7", "X-Retry-After": "13"}])
def test_thread_handler_preserves_shared_classification(error_handler, thread_error_handler, status, body, headers) -> None:
    response = requests.Response()
    response.status_code = status
    response.url = "https://api.usepylon.com/issues/synthetic-parent/threads"
    response._content = json.dumps(body).encode()
    response.headers.update(headers)
    if status == 400 and "code" not in body:
        assert thread_error_handler.interpret_response(response).response_action == ResponseAction.RETRY
        assert error_handler.interpret_response(response).response_action == ResponseAction.FAIL
    else:
        assert thread_error_handler.interpret_response(response) == error_handler.interpret_response(response)
    assert thread_error_handler.max_retries == 5
    assert thread_error_handler.backoff_strategies == error_handler.backoff_strategies
    for attempt in range(5):
        assert thread_error_handler.backoff_time(response, attempt_count=attempt) == error_handler.backoff_time(
            response, attempt_count=attempt
        )


@pytest.mark.parametrize("status", [200, 201, 204, 206])
@pytest.mark.parametrize("body", [{"data": []}, {"data": [], "code": "synthetic_error"}, {"data": [], "code": None}])
def test_thread_success_bodies_match_no_filters(error_handler, thread_error_handler, status, body) -> None:
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(body).encode()
    for handler in (error_handler, thread_error_handler):
        assert all(response_filter.matches(response) is None for response_filter in handler.response_filters)
        resolution = handler.interpret_response(response)
        assert resolution.response_action == ResponseAction.SUCCESS
        assert resolution.failure_type is None
        assert resolution.error_message is None
    assert thread_error_handler.interpret_response(response) == error_handler.interpret_response(response)


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


def test_retry_headers_precede_exponential_backoff(error_handler) -> None:
    assert error_handler.max_retries == 5
    assert len(error_handler.backoff_strategies) == 3
    retry_after, x_retry_after, exponential = error_handler.backoff_strategies
    response = requests.Response()
    response.status_code = 429
    response.headers["Retry-After"] = "7"
    response.headers["X-Retry-After"] = "13"
    assert retry_after.backoff_time(response, attempt_count=0) == 7
    assert x_retry_after.backoff_time(response, attempt_count=0) == 13
    assert error_handler.backoff_time(response, attempt_count=0) == 7
    response.headers.clear()
    assert retry_after.backoff_time(response, attempt_count=0) is None
    assert x_retry_after.backoff_time(response, attempt_count=0) is None
    assert [exponential.backoff_time(response, attempt_count=attempt) for attempt in range(3)] == [5, 10, 20]
    assert [error_handler.backoff_time(response, attempt_count=attempt) for attempt in range(3)] == [5, 10, 20]


@pytest.mark.parametrize(
    "headers,expected",
    [
        ({"Retry-After": "7"}, [7, 7, 7]),
        ({"X-Retry-After": "13"}, [13, 13, 13]),
        ({"Retry-After": "7", "X-Retry-After": "121"}, [7, 7, 7]),
        ({}, [5, 10, 20]),
    ],
)
def test_retry_header_fallback(error_handler: DefaultErrorHandler, headers: dict[str, str], expected: list[int]) -> None:
    response = requests.Response()
    response.status_code = 429
    response.headers.update(headers)
    assert [error_handler.backoff_time(response, attempt_count=attempt) for attempt in range(3)] == expected


@pytest.mark.parametrize("status", [400, 401, 403])
@pytest.mark.parametrize(
    "code,expected_text",
    [
        (
            "wrong_region_token",
            "Set Region to match the token: pylon_api_eu_ means EU, pylon_api_ means US, and older unprefixed tokens use the region where the Pylon tenant is hosted.",
        ),
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
@pytest.mark.parametrize("header", ["Retry-After", "X-Retry-After"])
def test_excessive_retry_after_stops_instead_of_waiting(error_handler: DefaultErrorHandler, header: str, header_value: str) -> None:
    response = requests.Response()
    response.status_code = 429
    response.headers[header] = header_value
    with pytest.raises(AirbyteTracedException) as exc:
        error_handler.backoff_time(response, attempt_count=0)
    assert exc.value.failure_type == FailureType.transient_error
