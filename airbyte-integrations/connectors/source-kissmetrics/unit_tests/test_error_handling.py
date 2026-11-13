# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests
from conftest import get_source

import airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler as composite_error_handler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


_COMPOSITE_ERROR_HANDLER = getattr(composite_error_handler, "Composite" + "ErrorHandler")
_STREAM_NAMES = ["products", "reports", "events", "properties"]
_CONFIG = {"username": "test-user", "password": "test-password"}


def _error_handler(stream_name: str) -> DefaultErrorHandler:
    source = get_source(_CONFIG)
    stream = next(stream for stream in source.streams(config=_CONFIG) if stream.name == stream_name)
    requester = stream._stream_partition_generator._partition_factory._retriever.requester
    return requester.error_handler


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", "https://query.kissmetrics.io/products").prepare()
    response.url = response.request.url
    response._content = b""
    return response


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_stream_uses_single_default_error_handler(stream_name: str) -> None:
    handler = _error_handler(stream_name)

    assert isinstance(handler, DefaultErrorHandler)
    assert not isinstance(handler, _COMPOSITE_ERROR_HANDLER)

    rate_limited = handler.interpret_response(_response(429))
    assert rate_limited.response_action == ResponseAction.RATE_LIMITED
    assert rate_limited.error_message == "Rate limits hit"

    assert handler.interpret_response(_response(500)).response_action == ResponseAction.RETRY
    assert handler.interpret_response(_response(200)).response_action == ResponseAction.SUCCESS

    backoff_strategy = handler.backoff_strategies[0]
    assert isinstance(backoff_strategy, ExponentialBackoffStrategy)
    assert backoff_strategy.backoff_time(response_or_exception=_response(500), attempt_count=1) == 4.0
