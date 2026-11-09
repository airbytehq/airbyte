# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import yaml
from conftest import _get_manifest_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_MANIFEST = yaml.safe_load(_MANIFEST_PATH.read_text())
_STREAMS = _MANIFEST["definitions"]["streams"]
_CONFIG = {"api_key": "token", "start_date": "2024-01-01T00:00:00Z"}


def _walk_nodes(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_nodes(value)


def _error_handlers(stream):
    for node in _walk_nodes(stream):
        if isinstance(node, dict) and "error_handler" in node:
            yield node["error_handler"]


def test_manifest_has_no_composite_error_handler() -> None:
    composite_error_handler = "Composite" + "ErrorHandler"

    assert not any(isinstance(node, dict) and node.get("type") == composite_error_handler for node in _walk_nodes(_MANIFEST))


@pytest.mark.parametrize("stream_name", tuple(_STREAMS))
def test_stream_error_handler_retries_rate_limits(stream_name: str) -> None:
    handlers_by_stream = {name: list(_error_handlers(stream)) for name, stream in _STREAMS.items()}
    assert sum(len(handlers) for handlers in handlers_by_stream.values()) == 12

    handlers = handlers_by_stream[stream_name]
    assert handlers
    for handler in handlers:
        assert handler["type"] == "DefaultErrorHandler"
        assert handler["max_retries"] == 3
        assert handler["backoff_strategies"] == [{"type": "ExponentialBackoffStrategy", "factor": 2}]
        assert handler["response_filters"] == [
            {
                "type": "HttpResponseFilter",
                "action": "RATE_LIMITED",
                "http_codes": [429],
                "error_message": "Rate limit hit",
            }
        ]


def test_user_stream_retries_rate_limited_response(monkeypatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
    user_request = HttpRequest(
        url="https://api.buildkite.com/v2/user",
        query_params="any query_parameters",
        headers={"Authorization": "Bearer token"},
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(
            user_request,
            [
                HttpResponse(body="{}", status_code=429),
                HttpResponse(body=json.dumps([{"id": 1}]), status_code=200),
            ],
        )
        catalog = CatalogBuilder().with_stream("user", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data["id"] for record in output.records] == [1]
        assert not output.errors
        http_mocker.assert_number_of_calls(user_request, 2)
