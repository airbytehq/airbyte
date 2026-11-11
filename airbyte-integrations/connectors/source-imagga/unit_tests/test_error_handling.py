# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


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


@pytest.mark.parametrize(
    "status_code, expected_action, expected_failure_type, expected_error_message",
    [
        (
            403,
            ResponseAction.SUCCESS,
            None,
            "You have reached your concurrent request limits for your subscription",
        ),
        (401, ResponseAction.FAIL, FailureType.config_error, None),
        (429, ResponseAction.RATE_LIMITED, None, None),
        (500, ResponseAction.RETRY, None, None),
    ],
)
def test_categorize_photos_error_handler(
    status_code: int,
    expected_action: ResponseAction,
    expected_failure_type: FailureType | None,
    expected_error_message: str | None,
) -> None:
    manifest = _resolved_manifest()
    definition = manifest["definitions"]["streams"]["categorize_photos"]["retriever"]["requester"]["error_handler"]

    assert definition["type"] == "DefaultErrorHandler"
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})
    assert handler.max_retries == 5

    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps({"message": "Imagga API response"}).encode()
    response.request = requests.Request("GET", "https://api.imagga.com/v2/categories/x").prepare()
    response.url = response.request.url

    resolution = handler.interpret_response(response)

    assert resolution.response_action == expected_action
    if expected_failure_type is not None:
        assert resolution.failure_type == expected_failure_type
    if expected_error_message is not None:
        assert resolution.error_message == expected_error_message
