# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

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
