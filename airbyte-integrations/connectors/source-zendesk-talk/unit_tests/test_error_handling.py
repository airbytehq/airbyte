# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the error handlers declared in `manifest.yaml`."""

import json
from typing import Any, Iterator

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG = {
    "subdomain": "example",
    "credentials": {"auth_type": "api_token", "email": "test@example.com", "api_token": "test_token"},
    "start_date": "2024-01-01T00:00:00Z",
}
ADDRESSES_REQUEST = HttpRequest(
    url="https://example.zendesk.com/api/v2/channels/voice/addresses",
    query_params=ANY_QUERY_PARAMS,
)
ERROR_HANDLER_STREAMS = [
    "addresses",
    "agents_activity",
    "agents_overview",
    "greeting_categories",
    "greetings",
    "phone_numbers",
    "call_legs",
    "calls",
    "current_queue_activity",
    "account_overview",
    "ivrs",
    "ivr_menus",
    "ivr_routes",
]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Skip real waits and record the requested durations."""
    slept: list[float] = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest() -> dict[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _walk(node: Any) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _without_parameters(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _without_parameters(value) for key, value in node.items() if key != "$parameters"}
    if isinstance(node, list):
        return [_without_parameters(value) for value in node]
    return node


def _read_addresses(expecting_exception: bool = False) -> Any:
    catalog = CatalogBuilder().with_stream("addresses", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


def test_every_error_handler_is_a_single_default_error_handler() -> None:
    manifest = _resolved_manifest()
    error_handlers = [node["error_handler"] for node in _walk(manifest) if "error_handler" in node]

    assert error_handlers
    assert {handler["type"] for handler in error_handlers} == {"DefaultErrorHandler"}


@pytest.mark.parametrize("stream_name", ERROR_HANDLER_STREAMS)
def test_stream_error_handler_is_default_with_retry_after_backoff(stream_name: str) -> None:
    manifest = _resolved_manifest()
    streams = manifest["definitions"]["streams"]
    requester_streams = {
        name
        for name, stream in streams.items()
        if isinstance(stream.get("retriever"), dict) and isinstance(stream["retriever"].get("requester"), dict)
    }
    assert set(ERROR_HANDLER_STREAMS) == requester_streams

    error_handler = streams[stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert _without_parameters(error_handler["backoff_strategies"]) == [{"type": "WaitTimeFromHeader", "header": "Retry-After"}]
    assert "response_filters" not in error_handler
    assert "max_retries" not in error_handler


def test_429_waits_for_retry_after_and_recovers(no_sleep: list[float]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            ADDRESSES_REQUEST,
            [
                HttpResponse(body="{}", status_code=429, headers={"Retry-After": "7"}),
                HttpResponse(body=json.dumps({"addresses": [{"id": 1, "name": "Main"}]}), status_code=200),
            ],
        )

        output = _read_addresses()

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1]
        http_mocker.assert_number_of_calls(ADDRESSES_REQUEST, 2)
        assert 8.0 in no_sleep


def test_500_retries_and_recovers() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            ADDRESSES_REQUEST,
            [
                HttpResponse(body="{}", status_code=500),
                HttpResponse(body=json.dumps({"addresses": [{"id": 1, "name": "Main"}]}), status_code=200),
            ],
        )

        output = _read_addresses()

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1]
        http_mocker.assert_number_of_calls(ADDRESSES_REQUEST, 2)


def test_404_fails_sync() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(ADDRESSES_REQUEST, HttpResponse(body="{}", status_code=404))

        output = _read_addresses(expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(ADDRESSES_REQUEST, 1)
