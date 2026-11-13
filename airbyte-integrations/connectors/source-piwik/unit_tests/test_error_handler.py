# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


_STREAM_NAMES = list(yaml.safe_load(_YAML_FILE_PATH.read_text())["definitions"]["streams"])


def test_manifest_has_no_composite_error_handler(manifest: dict) -> None:
    assert "CompositeErrorHandler" not in json.dumps(manifest)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_stream_error_handler(manifest: dict, stream_name: str) -> None:
    handler_definition = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    assert handler_definition == {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "RATE_LIMITED",
                "http_codes": [429],
                "error_message": "Rate limits hit",
            }
        ],
    }
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, config={})
    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 3
    for status, action in [(200, ResponseAction.SUCCESS), (429, ResponseAction.RATE_LIMITED), (500, ResponseAction.RETRY)]:
        response = requests.Response()
        response.status_code = status
        response._content = b"{}"
        resolution = handler.interpret_response(response)
        assert resolution.response_action == action
        if status == 429:
            assert resolution.error_message == "Rate limits hit"
        if status != 200:
            assert handler.backoff_time(response, attempt_count=1) == 4
