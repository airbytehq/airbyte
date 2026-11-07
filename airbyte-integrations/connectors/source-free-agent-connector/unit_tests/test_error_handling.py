# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


DEFAULT_BACKOFF_STRATEGIES = [{"type": "WaitTimeFromHeader", "header": "Retry-After"}]


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _error_handler_definition(stream_name: str):
    manifest = _resolved_manifest()
    return manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]


def _error_handler(stream_name: str):
    definition = _error_handler_definition(stream_name)
    assert definition["type"] == "DefaultErrorHandler"
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})


def _response(status_code: int, headers: dict[str, str] | None = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    response.headers.update(headers or {})
    response._content = json.dumps({"message": "FreeAgent API response"}).encode()
    response.request = requests.Request("GET", "https://api.freeagent.com/v2/users").prepare()
    response.url = response.request.url
    return response


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "Composite" + "ErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not composite_handlers


@pytest.mark.parametrize("stream_name", list(_resolved_manifest()["definitions"]["streams"]))
def test_streams_use_default_error_handler_with_retry_after_backoff(stream_name: str) -> None:
    definition = _error_handler_definition(stream_name)

    assert definition["type"] == "DefaultErrorHandler"
    assert definition["backoff_strategies"] == DEFAULT_BACKOFF_STRATEGIES


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (404, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
        (200, ResponseAction.SUCCESS),
    ],
)
def test_users_error_handler(status_code: int, expected_action: ResponseAction) -> None:
    handler = _error_handler("Users")

    assert handler.max_retries == 5
    resolution = handler.interpret_response(_response(status_code))

    assert resolution.response_action == expected_action


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (404, ResponseAction.IGNORE),
        (500, ResponseAction.RETRY),
        (429, ResponseAction.RATE_LIMITED),
    ],
)
def test_payslips_error_handler(status_code: int, expected_action: ResponseAction) -> None:
    resolution = _error_handler("Payslips").interpret_response(_response(status_code))

    assert resolution.response_action == expected_action


def test_users_error_handler_honors_retry_after_header() -> None:
    handler = _error_handler("Users")
    response = _response(429, {"Retry-After": "7"})

    assert handler.backoff_strategies[0].backoff_time(response, 1) == 7
