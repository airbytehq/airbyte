# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import requests
from _helpers import get_source

from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


_CONFIG = {
    "username": "test_user",
    "password": "test_password",
    "domain_name": "test",
    "start_date": "2024-01-01T00:00:00Z",
}


def _error_handlers(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "error_handler":
                yield value
            yield from _error_handlers(value)
    elif isinstance(node, list):
        for item in node:
            yield from _error_handlers(item)


def test_every_stream_uses_a_single_default_error_handler():
    resolved_manifest = get_source(_CONFIG).resolved_manifest

    error_handler_types = {error_handler["type"] for error_handler in _error_handlers(resolved_manifest)}
    assert error_handler_types == {"DefaultErrorHandler"}
    assert len(resolved_manifest["streams"]) == 18

    factory = ModelToComponentFactory()
    response = requests.Response()
    response.status_code = 429
    response._content = b"{}"

    for stream in resolved_manifest["streams"]:
        error_handler = stream["retriever"]["requester"]["error_handler"]
        assert error_handler["type"] == "DefaultErrorHandler", stream["name"]
        assert "error_handlers" not in error_handler, stream["name"]
        assert error_handler["max_retries"] == 3, stream["name"]
        assert error_handler["backoff_strategies"] == [{"type": "ExponentialBackoffStrategy", "factor": 2}], stream["name"]
        assert error_handler["response_filters"] == [
            {"type": "HttpResponseFilter", "action": "RATE_LIMITED", "http_codes": [429], "error_message": "Rate limits hit"}
        ], stream["name"]

        handler = factory.create_component(DefaultErrorHandlerModel, error_handler, _CONFIG)
        assert isinstance(handler, DefaultErrorHandler), stream["name"]
        assert handler.max_retries == 3, stream["name"]
        assert len(handler.backoff_strategies) == 1, stream["name"]
        strategy = handler.backoff_strategies[0]
        assert isinstance(strategy, ExponentialBackoffStrategy), stream["name"]
        assert strategy.backoff_time(response, attempt_count=3) == 16, stream["name"]
        assert handler.interpret_response(response).response_action == ResponseAction.RATE_LIMITED, stream["name"]
