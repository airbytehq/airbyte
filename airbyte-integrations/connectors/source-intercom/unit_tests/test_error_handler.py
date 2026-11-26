# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import patch

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CustomErrorHandler as CustomErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import (
    ManifestReferenceResolver,
)
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import (
    ModelToComponentFactory,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


def _conversation_parts_error_handler(manifest_path: Path) -> dict[str, Any]:
    manifest = yaml.safe_load(manifest_path.read_text())
    resolved_manifest = ManifestReferenceResolver().preprocess_manifest(manifest)
    return resolved_manifest["definitions"]["streams"]["conversation_parts"]["retriever"]["requester"]["error_handler"]


def _build_error_handler(definition: dict[str, Any], components_module: ModuleType) -> DefaultErrorHandler:
    package = ModuleType("source_declarative_manifest")
    package.__path__ = []
    package.components = components_module
    sys.modules[package.__name__] = package
    sys.modules[f"{package.__name__}.components"] = components_module
    return ModelToComponentFactory().create_component(CustomErrorHandlerModel, definition, config={})


def test_conversation_parts_error_handler_is_not_composite(manifest_path: Path, components_module: ModuleType) -> None:
    definition = _conversation_parts_error_handler(manifest_path)

    assert definition["type"] == "CustomErrorHandler"
    assert definition["class_name"].endswith("ErrorHandlerWithRateLimiter")
    assert "Composite" + "ErrorHandler" not in manifest_path.read_text()

    handler = _build_error_handler(definition, components_module)
    assert isinstance(handler, components_module.ErrorHandlerWithRateLimiter)
    assert handler.max_retries == 5


@pytest.mark.parametrize(
    ("status_code", "expected_action"),
    [
        (200, ResponseAction.SUCCESS),
        (404, ResponseAction.IGNORE),
        (401, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
    ],
)
def test_conversation_parts_error_resolution(
    manifest_path: Path,
    components_module: ModuleType,
    status_code: int,
    expected_action: ResponseAction,
) -> None:
    definition = _conversation_parts_error_handler(manifest_path)
    handler = _build_error_handler(definition, components_module)
    response = requests.Response()
    response.status_code = status_code
    response.headers = {}

    with patch.object(components_module.IntercomRateLimiter, "backoff_time") as backoff_time_mock:
        resolution = handler.interpret_response(response)
        backoff_time_mock.assert_called_once()

    assert resolution.response_action == expected_action
    if status_code == 401:
        assert resolution.failure_type == FailureType.config_error
        assert "Read conversations" in resolution.error_message


STREAM_NAMES = [
    "activity_logs",
    "admins",
    "tags",
    "teams",
    "segments",
    "companies",
    "company_attributes",
    "contact_attributes",
    "contacts",
    "conversations",
    "conversation_parts",
    "company_segments",
    "tickets",
]


def _stream_error_handler(manifest_path: Path, stream_name: str) -> dict[str, Any]:
    manifest = yaml.safe_load(manifest_path.read_text())
    resolved_manifest = ManifestReferenceResolver().preprocess_manifest(manifest)
    return resolved_manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]


def _response(status_code: int, body: Any) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers = {"Content-Type": "application/json"}
    response._content = json.dumps(body).encode()
    response.url = "https://api.intercom.io/tags"
    return response


def _interpret(manifest_path: Path, components_module: ModuleType, stream_name: str, response: requests.Response):
    definition = _stream_error_handler(manifest_path, stream_name)
    if definition["type"] == "DefaultErrorHandler":
        handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})
    else:
        handler = _build_error_handler(definition, components_module)
    with patch.object(components_module.IntercomRateLimiter, "backoff_time"):
        return handler.interpret_response(response)


def _intercom_error(code: str, message: str) -> dict[str, Any]:
    return {"type": "error.list", "request_id": "req", "errors": [{"code": code, "message": message}]}


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
@pytest.mark.parametrize(
    ("code", "message"),
    [("unauthorized", "Access Token Invalid"), ("token_not_found", "Token not found")],
)
def test_invalid_token_fails_with_reauthentication_message(
    manifest_path: Path, components_module: ModuleType, stream_name: str, code: str, message: str
) -> None:
    resolution = _interpret(manifest_path, components_module, stream_name, _response(401, _intercom_error(code, message)))

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert f'Intercom rejected the access token: "{message}"' in resolution.error_message
    assert "Re-authenticate the Intercom source" in resolution.error_message
    assert "Permission Scope Error" not in resolution.error_message


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
@pytest.mark.parametrize(
    "body",
    [_intercom_error("token_unauthorized", "Not authorized to access resource"), {}],
    ids=["token_unauthorized", "empty_body"],
)
def test_other_401_keeps_the_permission_message(
    manifest_path: Path, components_module: ModuleType, stream_name: str, body: dict[str, Any]
) -> None:
    resolution = _interpret(manifest_path, components_module, stream_name, _response(401, body))

    # tickets ignores a 401 so that workspaces without the Tickets permission still sync the other streams.
    expected_action = ResponseAction.IGNORE if stream_name == "tickets" else ResponseAction.FAIL
    assert resolution.response_action == expected_action
    assert "Permission Scope Error" in resolution.error_message


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
@pytest.mark.parametrize(
    "body",
    [{"type": "list", "data": [{"id": "1"}]}, [{"id": "1"}], {"type": "error.list", "errors": []}, {"errors": [None]}],
    ids=["object", "array", "empty_errors", "null_error"],
)
def test_success_response_does_not_match_the_invalid_token_filter(
    manifest_path: Path, components_module: ModuleType, stream_name: str, body: Any
) -> None:
    resolution = _interpret(manifest_path, components_module, stream_name, _response(200, body))

    assert resolution.response_action == ResponseAction.SUCCESS
