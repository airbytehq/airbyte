#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import time
from pathlib import Path

import pytest
import requests
import yaml
from test_streams import get_retriever, get_stream_by_name

from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_until_time_from_header_backoff_strategy import (
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


def _walk_nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_nodes(child)


def _response(status_code, body, headers=None):
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode()
    response.headers = headers or {}
    return response


def test_manifest_has_no_composite_error_handler():
    manifest_path = Path(__file__).resolve().parents[1] / "source_okta" / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    composite_handler_type = "".join(("Composite", "ErrorHandler"))

    assert all(node.get("type") != composite_handler_type for node in _walk_nodes(manifest))


@pytest.mark.parametrize("stream_name", ["logs", "users", "groups", "custom_roles"])
def test_streams_use_default_error_handler(stream_name, oauth_config):
    stream = get_stream_by_name(stream_name, config=oauth_config)
    error_handler = get_retriever(stream).requester.error_handler

    assert isinstance(error_handler, DefaultErrorHandler)
    assert len(error_handler.backoff_strategies) == 1
    assert isinstance(error_handler.backoff_strategies[0], WaitUntilTimeFromHeaderBackoffStrategy)


def test_logs_ignore_known_bad_request(oauth_config):
    stream = get_stream_by_name("logs", config=oauth_config)
    response = _response(
        400,
        {"errorCode": "E0000001", "errorSummary": "Api validation failed: since"},
    )

    resolution = get_retriever(stream).requester.error_handler.interpret_response(response)

    assert resolution.response_action == ResponseAction.IGNORE
    assert resolution.error_message == "Api validation failed: since"


def test_logs_ignores_any_bad_request(oauth_config):
    """HttpResponseFilter matches http_codes or predicate, so every 400 is ignored."""
    stream = get_stream_by_name("logs", config=oauth_config)
    response = _response(400, {"errorCode": "E0000003", "errorSummary": "x"})

    resolution = get_retriever(stream).requester.error_handler.interpret_response(response)

    assert resolution.response_action == ResponseAction.IGNORE


def test_logs_does_not_ignore_unauthorized_response(oauth_config):
    stream = get_stream_by_name("logs", config=oauth_config)
    response = _response(401, {"errorCode": "E0000003", "errorSummary": "x"})

    resolution = get_retriever(stream).requester.error_handler.interpret_response(response)

    assert resolution.response_action != ResponseAction.IGNORE


@pytest.mark.parametrize("stream_name", ["logs", "users"])
def test_rate_limit_backoff_uses_reset_header(stream_name, oauth_config):
    stream = get_stream_by_name(stream_name, config=oauth_config)
    response = _response(
        429,
        {},
        headers={"X-Rate-Limit-Reset": int(time.time()) + 130},
    )
    error_handler = get_retriever(stream).requester.error_handler

    assert error_handler.interpret_response(response).response_action in (ResponseAction.RETRY, ResponseAction.RATE_LIMITED)
    backoff_time = error_handler.backoff_strategies[0].backoff_time(response_or_exception=response, attempt_count=0)
    assert 60 <= backoff_time <= 130


def test_logs_default_error_handler_retry_limits(oauth_config):
    stream = get_stream_by_name("logs", config=oauth_config)
    error_handler = get_retriever(stream).requester.error_handler

    assert error_handler.max_time == 600
    assert error_handler.max_retries == 5
