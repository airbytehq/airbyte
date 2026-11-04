# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import pytest
import requests
from conftest import get_source
from mock_server.config import ConfigBuilder

from airbyte_cdk.sources.declarative.models import declarative_component_schema
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import WaitTimeFromHeaderBackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


CONFIG = ConfigBuilder().with_account_id("123456").with_api_token("t").build()
RESOLVED_MANIFEST = get_source(config=CONFIG).resolved_manifest
HANDLED_STREAM_NAMES = [stream["name"] for stream in RESOLVED_MANIFEST["streams"] if stream["name"] != "company"]
RESPONSE_CASES = [
    (200, ResponseAction.SUCCESS),
    (401, ResponseAction.IGNORE),
    (403, ResponseAction.IGNORE),
    (404, ResponseAction.IGNORE),
    (429, ResponseAction.RATE_LIMITED),
    (500, ResponseAction.RETRY),
    (502, ResponseAction.RETRY),
    (503, ResponseAction.RETRY),
    (400, ResponseAction.FAIL),
    (402, ResponseAction.RETRY),
]


def _walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _requester(stream_name: str) -> dict:
    return next(stream for stream in RESOLVED_MANIFEST["streams"] if stream["name"] == stream_name)["retriever"]["requester"]


def _handler_definition(stream_name: str) -> dict:
    return _requester(stream_name)["error_handler"]


def _error_handler(stream_name: str):
    definition = _handler_definition(stream_name)
    model_type = (
        DefaultErrorHandlerModel
        if definition["type"] == "DefaultErrorHandler"
        else getattr(declarative_component_schema, definition["type"])
    )
    return ModelToComponentFactory().create_component(model_type, definition, config=CONFIG)


def _response(status_code: int, headers: dict[str, str] | None = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers.update(headers or {})
    response._content = b"{}"
    response.request = requests.Request("GET", "https://api.harvestapp.com/v2/example").prepare()
    response.url = response.request.url
    return response


def _filter_message(definition: dict, status_code: int) -> str:
    if definition["type"] == "Composite" + "ErrorHandler":
        error_handlers = definition["error_handlers"]
        filters = [filter_ for handler in error_handlers for filter_ in handler.get("response_filters", [])]
    else:
        filters = definition.get("response_filters", [])
    return next(filter_["error_message"] for filter_ in filters if status_code in filter_.get("http_codes", []))


def test_manifest_uses_shared_default_error_handler() -> None:
    assert not any(node.get("type") == "Composite" + "ErrorHandler" for node in _walk(RESOLVED_MANIFEST))

    streams = RESOLVED_MANIFEST["streams"]
    for stream in streams:
        requester = stream["retriever"]["requester"]
        if stream["name"] == "company":
            assert "error_handler" not in requester
        else:
            assert requester["error_handler"]["type"] == "DefaultErrorHandler"
            assert "error_handlers" not in requester["error_handler"]

    assert sum("error_handler" in stream["retriever"]["requester"] for stream in streams) == 31


@pytest.mark.parametrize("stream_name", HANDLED_STREAM_NAMES)
@pytest.mark.parametrize(("status_code", "expected_action"), RESPONSE_CASES)
def test_each_stream_classifies_responses(
    stream_name: str,
    status_code: int,
    expected_action: ResponseAction,
) -> None:
    definition = _handler_definition(stream_name)
    resolution = _error_handler(stream_name).interpret_response(_response(status_code))

    assert resolution.response_action == expected_action
    if status_code in {401, 403, 404}:
        assert resolution.error_message == _filter_message(definition, status_code)


@pytest.mark.parametrize("stream_name", HANDLED_STREAM_NAMES)
def test_each_stream_retries_with_retry_after(stream_name: str) -> None:
    handler = _error_handler(stream_name)

    assert handler.max_retries == 5
    assert handler.max_time == 600
    assert len(handler.backoff_strategies) == 1
    backoff_strategy = handler.backoff_strategies[0]
    assert isinstance(backoff_strategy, WaitTimeFromHeaderBackoffStrategy)
    assert backoff_strategy.backoff_time(_response(429, {"Retry-After": "7"}), attempt_count=1) == 7
    assert backoff_strategy.backoff_time(_response(429), attempt_count=1) is None
