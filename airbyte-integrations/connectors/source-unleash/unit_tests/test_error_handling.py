# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Test Unleash's manifest error handling and retry behavior."""

import json
import time
from typing import Any, Mapping

import pytest
import requests
import yaml

import airbyte_cdk.sources.declarative.models.declarative_component_schema as declarative_component_schema
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .conftest import _YAML_FILE_PATH, get_source


CONFIG: Mapping[str, Any] = {
    "api_token": "test-token",
    "api_url": "unleash.example.com",
    "project_name": "default",
    "nameprefix": "feat",
}
FEATURES_URL = "https://unleash.example.com/api/client/features"
FEATURES_REQUEST = HttpRequest(
    url=FEATURES_URL,
    query_params={"project": "default", "namePrefix": "feat"},
    headers={"Authorization": "test-token"},
)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Skip real waits and record requested durations."""
    slept: list[float] = []
    monkeypatch.setattr(time, "sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest() -> dict[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _features_error_handler_definition() -> dict[str, Any]:
    manifest = _resolved_manifest()
    stream = next(stream for stream in manifest["streams"] if stream["name"] == "features")
    return stream["retriever"]["requester"]["error_handler"]


def _error_handler():
    definition = _features_error_handler_definition()
    handler_model = getattr(declarative_component_schema, definition["type"])
    return ModelToComponentFactory().create_component(handler_model, definition, config=CONFIG)


def _configured_default_error_handler():
    definition = _features_error_handler_definition()
    if definition["type"] == "Composite" + "ErrorHandler":
        definition = definition["error_handlers"][0]
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", FEATURES_URL).prepare()
    response.url = FEATURES_URL
    response.headers["Content-Type"] = "application/json"
    response._content = b"{}"
    return response


def _error_trace(output: EntrypointOutput):
    assert output.errors, "expected the sync to emit an error trace"
    return output.errors[0].trace.error


def _read_features(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("features", SyncMode.full_refresh).build()
    return read(
        get_source(CONFIG),
        CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


def _features_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"version": 2, "features": [{"name": "f1"}]}), status_code=200)


def _error_response(status_code: int) -> HttpResponse:
    return HttpResponse(body=json.dumps({}), status_code=status_code)


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "Composite" + "ErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert not composite_handlers


@pytest.mark.parametrize(
    "status_code, expected_action, expected_failure_type, expected_message",
    [
        (401, ResponseAction.FAIL, FailureType.config_error, "Unleash rejected the API token"),
        (403, ResponseAction.RETRY, FailureType.config_error, "Unleash denied access"),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error, "Unleash rate limit reached"),
        (400, ResponseAction.FAIL, FailureType.system_error, None),
        (404, ResponseAction.FAIL, FailureType.system_error, None),
        (500, ResponseAction.RETRY, FailureType.transient_error, None),
        (502, ResponseAction.RETRY, FailureType.transient_error, None),
        (503, ResponseAction.RETRY, FailureType.transient_error, None),
        (402, ResponseAction.RETRY, None, None),
    ],
)
def test_handler_classifies_http_status(
    status_code: int,
    expected_action: ResponseAction,
    expected_failure_type: FailureType | None,
    expected_message: str | None,
) -> None:
    resolution = _error_handler().interpret_response(_response(status_code))

    assert resolution.response_action == expected_action
    if expected_failure_type is not None:
        assert resolution.failure_type == expected_failure_type
    if expected_message is not None:
        assert expected_message in (resolution.error_message or "")


def test_max_retries_and_backoff() -> None:
    handler = _configured_default_error_handler()
    assert handler.max_retries == 3

    strategy = handler.backoff_strategies[0]
    factor = float(strategy.factor)
    assert factor == 2
    response = _response(500)
    backoff_values = [strategy.backoff_time(response_or_exception=response, attempt_count=attempt) for attempt in range(1, 4)]
    first_backoff = backoff_values[0]

    assert backoff_values == [first_backoff * factor**offset for offset in range(3)]


def test_401_fails_with_actionable_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(FEATURES_REQUEST, _error_response(401))

        output = _read_features(expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "Unleash rejected the API token" in error.message
        http_mocker.assert_number_of_calls(FEATURES_REQUEST, 1)


def test_403_retries_then_returns_records() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(FEATURES_REQUEST, [_error_response(403), _features_response()])

        output = _read_features()

        assert not output.errors
        assert [record.record.data["name"] for record in output.records] == ["f1"]
        http_mocker.assert_number_of_calls(FEATURES_REQUEST, 2)


def test_403_exhausts_retries_and_surfaces_actionable_message() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(FEATURES_REQUEST, _error_response(403))

        output = _read_features(expecting_exception=True)

        error = _error_trace(output)
        # The CDK reports exhausted retries as system_error regardless of the filter's failure_type.
        assert error.failure_type == FailureType.system_error
        assert "Unleash denied access" in error.internal_message or output.is_in_logs("Unleash denied access")
        http_mocker.assert_number_of_calls(FEATURES_REQUEST, 4)


def test_429_retries_then_returns_records() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(FEATURES_REQUEST, [_error_response(429), _features_response()])

        output = _read_features()

        assert not output.errors
        assert [record.record.data["name"] for record in output.records] == ["f1"]
        http_mocker.assert_number_of_calls(FEATURES_REQUEST, 2)


def test_429_exhausts_retries_with_actionable_message() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(FEATURES_REQUEST, _error_response(429))

        output = _read_features(expecting_exception=True)

        error = _error_trace(output)
        assert "Unleash rate limit reached" in error.message or output.is_in_logs("Unleash rate limit reached")
        http_mocker.assert_number_of_calls(FEATURES_REQUEST, 4)


def test_500_retries_then_returns_records() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(FEATURES_REQUEST, [_error_response(500), _features_response()])

        output = _read_features()

        assert not output.errors
        assert [record.record.data["name"] for record in output.records] == ["f1"]
        http_mocker.assert_number_of_calls(FEATURES_REQUEST, 2)
