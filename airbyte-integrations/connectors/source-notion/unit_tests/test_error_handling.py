#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import json
from pathlib import Path

import pytest
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_SHARED_HANDLER_STREAMS = ["pages", "data_sources", "comments", "blocks"]

_INVALID_START_CURSOR_MESSAGE = "The start_cursor provided is invalid: 0c9d1a2b-1234."
_NOT_SHARED_MESSAGE = (
    "Could not find page with ID: 0c9d1a2b-1234. Make sure the relevant pages and databases are shared with your integration."
)
_RESTRICTED_USERS_MESSAGE = (
    "Notion integration lacks read user information for the Users stream. Enable it in Notion or disable the Users stream."
)


def _error_handler(stream_name):
    source = get_source(_CONFIG)
    stream = next(stream for stream in source.streams(_CONFIG) if stream.name == stream_name)
    return stream._stream_partition_generator._partition_factory._retriever.requester.error_handler


def _notion_response(status_code, code=None, message=None, headers=None):
    response = requests.Response()
    response.status_code = status_code
    response.headers.update({"Content-Type": "application/json", **(headers or {})})
    body = {"object": "list", "results": []} if status_code == 200 else {"object": "error", "status": status_code}
    if code:
        body["code"] = code
    if message:
        body["message"] = message
    response._content = json.dumps(body).encode()
    return response


def test_manifest_has_no_composite_error_handler():
    assert "CompositeErrorHandler" not in Path(_YAML_FILE_PATH).read_text()


@pytest.mark.parametrize("stream_name", _SHARED_HANDLER_STREAMS + ["users"])
def test_each_stream_uses_a_single_default_error_handler(stream_name):
    error_handler = _error_handler(stream_name)
    assert type(error_handler) is DefaultErrorHandler
    assert error_handler.max_retries == 5


@pytest.mark.parametrize("stream_name", _SHARED_HANDLER_STREAMS)
@pytest.mark.parametrize(
    "status_code, code, message, expected_action",
    [
        pytest.param(200, None, None, ResponseAction.SUCCESS, id="200_success"),
        pytest.param(400, "validation_error", _INVALID_START_CURSOR_MESSAGE, ResponseAction.IGNORE, id="400_invalid_start_cursor_ignored"),
        # HttpResponseFilter matches on status code OR message, so every 400 is ignored, as on 4.0.30.
        pytest.param(400, "validation_error", "body failed validation.", ResponseAction.IGNORE, id="400_other_message_ignored"),
        pytest.param(404, "object_not_found", _NOT_SHARED_MESSAGE, ResponseAction.IGNORE, id="404_not_shared_ignored"),
        pytest.param(404, "object_not_found", "Not found.", ResponseAction.IGNORE, id="404_other_message_ignored"),
        pytest.param(403, "restricted_resource", _NOT_SHARED_MESSAGE, ResponseAction.IGNORE, id="403_not_shared_message_ignored"),
        pytest.param(403, "restricted_resource", "Insufficient permissions.", ResponseAction.FAIL, id="403_fails"),
        pytest.param(401, "unauthorized", "API token is invalid.", ResponseAction.FAIL, id="401_fails"),
        pytest.param(429, "rate_limited", "You have been rate limited.", ResponseAction.RATE_LIMITED, id="429_rate_limited"),
        pytest.param(429, "rate_limited", _NOT_SHARED_MESSAGE, ResponseAction.RATE_LIMITED, id="429_wins_over_message_ignore"),
        pytest.param(408, None, None, ResponseAction.RETRY, id="408_retried"),
        pytest.param(409, "conflict_error", "Conflict occurred.", ResponseAction.RETRY, id="409_retried"),
        pytest.param(500, "internal_server_error", "Unexpected error.", ResponseAction.RETRY, id="500_retried"),
        pytest.param(502, "bad_gateway", None, ResponseAction.RETRY, id="502_retried"),
        pytest.param(503, "service_unavailable", None, ResponseAction.RETRY, id="503_retried"),
        pytest.param(504, "gateway_timeout", None, ResponseAction.RETRY, id="504_retried"),
        pytest.param(529, "service_overload", None, ResponseAction.RETRY, id="529_retried"),
    ],
)
def test_shared_error_handler_classifies_each_status(stream_name, status_code, code, message, expected_action):
    resolution = _error_handler(stream_name).interpret_response(_notion_response(status_code, code, message))
    assert resolution.response_action == expected_action


@pytest.mark.parametrize(
    "status_code, code, message, expected_action, expected_failure_type, expected_message",
    [
        pytest.param(200, None, None, ResponseAction.SUCCESS, None, None, id="200_success"),
        pytest.param(
            403,
            "restricted_resource",
            "Insufficient permissions for this endpoint.",
            ResponseAction.FAIL,
            FailureType.config_error,
            _RESTRICTED_USERS_MESSAGE,
            id="403_restricted_resource_config_error",
        ),
        pytest.param(429, "restricted_resource", None, ResponseAction.RATE_LIMITED, None, None, id="429_wins_over_restricted_resource"),
        pytest.param(429, "rate_limited", "You have been rate limited.", ResponseAction.RATE_LIMITED, None, None, id="429_rate_limited"),
        pytest.param(400, "validation_error", _INVALID_START_CURSOR_MESSAGE, ResponseAction.FAIL, None, None, id="400_not_ignored"),
        pytest.param(404, "object_not_found", _NOT_SHARED_MESSAGE, ResponseAction.FAIL, None, None, id="404_not_ignored"),
        pytest.param(500, "internal_server_error", None, ResponseAction.RETRY, None, None, id="500_retried"),
        pytest.param(529, "service_overload", None, ResponseAction.RETRY, None, None, id="529_retried"),
    ],
)
def test_users_error_handler_classifies_each_status(status_code, code, message, expected_action, expected_failure_type, expected_message):
    resolution = _error_handler("users").interpret_response(_notion_response(status_code, code, message))
    assert resolution.response_action == expected_action
    if expected_failure_type:
        assert resolution.failure_type == expected_failure_type
    if expected_message:
        assert resolution.error_message == expected_message


@pytest.mark.parametrize("stream_name", _SHARED_HANDLER_STREAMS + ["users"])
@pytest.mark.parametrize("status_code", [429, 529])
def test_backoff_waits_for_retry_after_header(stream_name, status_code):
    response = _notion_response(status_code, headers={"Retry-After": "7"})
    (backoff_strategy,) = _error_handler(stream_name).backoff_strategies
    assert backoff_strategy.backoff_time(response, attempt_count=1) == 7
