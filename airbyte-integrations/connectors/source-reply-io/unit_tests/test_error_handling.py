# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


STREAM_NAMES = ("campaigns", "email_accounts", "people", "templates")


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _handler_definitions(manifest, stream_name):
    definition = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    stream = next(stream for stream in manifest["streams"] if stream["name"] == stream_name)
    return definition, stream["retriever"]["requester"]["error_handler"]


def _make_response(status_code, body):
    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(body).encode()
    response.request = requests.Request("GET", "https://api.reply.io/v1/campaigns").prepare()
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


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_error_handler_definitions(stream_name: str) -> None:
    manifest = _resolved_manifest()

    for definition in _handler_definitions(manifest, stream_name):
        assert definition["type"] == "DefaultErrorHandler"
        handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})
        assert handler.max_retries == 5


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_error_handler_response_behavior(stream_name: str) -> None:
    manifest = _resolved_manifest()

    for definition in _handler_definitions(manifest, stream_name):
        handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})
        throttled_response = _make_response(200, "Too much requests. Please try again later.")

        assert handler.interpret_response(throttled_response).response_action == ResponseAction.RETRY
        assert handler.backoff_time(response_or_exception=throttled_response, attempt_count=1) == 15
        assert handler.interpret_response(_make_response(401, {"message": "Unauthorized"})).response_action == ResponseAction.FAIL
        assert handler.interpret_response(_make_response(500, {"message": "Server error"})).response_action == ResponseAction.RETRY
