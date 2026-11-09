# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "max_retries": 2,
    "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 5}],
    "response_filters": [{"type": "HttpResponseFilter", "action": "RATE_LIMITED", "error_message": "429"}],
}


def _resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _without_parameter_keys(node: object) -> object:
    if isinstance(node, dict):
        return {key: _without_parameter_keys(value) for key, value in node.items() if not key.startswith("$")}
    if isinstance(node, list):
        return [_without_parameter_keys(value) for value in node]
    return node


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    composite_handlers = []

    def walk(node: object) -> None:
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


def test_every_stream_uses_single_default_error_handler() -> None:
    manifest = _resolved_manifest()
    streams = manifest["definitions"]["streams"]

    assert len(streams) == 30
    for stream in streams.values():
        definition = stream["retriever"]["requester"]["error_handler"]
        assert _without_parameter_keys(definition) == EXPECTED_ERROR_HANDLER


@pytest.mark.parametrize(
    "status_code, expected_action, expected_failure_type",
    [
        (200, ResponseAction.SUCCESS, None),
        (400, ResponseAction.FAIL, FailureType.system_error),
        (401, ResponseAction.FAIL, FailureType.config_error),
        (403, ResponseAction.FAIL, FailureType.config_error),
        (404, ResponseAction.FAIL, FailureType.system_error),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        (500, ResponseAction.RETRY, FailureType.transient_error),
        (502, ResponseAction.RETRY, FailureType.transient_error),
    ],
)
def test_dashboards_error_handler_resolution(
    status_code: int,
    expected_action: ResponseAction,
    expected_failure_type: FailureType | None,
) -> None:
    manifest = _resolved_manifest()
    definition = manifest["definitions"]["streams"]["dashboards"]["retriever"]["requester"]["error_handler"]
    assert definition["type"] == "DefaultErrorHandler"
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})

    assert handler.max_retries == 2
    assert len(handler.backoff_strategies) == 1
    assert type(handler.backoff_strategies[0]).__name__ == "ConstantBackoffStrategy"
    assert handler.backoff_strategies[0].backoff_time_in_seconds.eval({}) == 5

    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps({"errors": [{"title": "x"}]}).encode()
    response.request = requests.Request("GET", "https://api.rootly.com/v1/dashboards").prepare()
    response.url = response.request.url

    resolution = handler.interpret_response(response)

    assert resolution.response_action == expected_action
    assert resolution.failure_type == expected_failure_type
