# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG = {"domain_name": "example.freshservice.com", "api_key": "test-api-key", "start_date": "2024-01-01T00:00:00Z"}
BASE_URL = "https://example.freshservice.com/api/v2"


def requester_handlers(node: Any, path: str = "") -> Iterator[tuple[str, Mapping[str, Any], str]]:
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}/{key}"
            if key == "error_handler":
                yield child_path, value, node["path"]
            else:
                yield from requester_handlers(value, child_path)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from requester_handlers(value, f"{path}/{index}")


@pytest.fixture(scope="session")
def manifest(manifest_path: Path) -> Mapping[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))


@pytest.fixture(scope="session")
def handlers(manifest: Mapping[str, Any]) -> Mapping[str, tuple[str, DefaultErrorHandler]]:
    factory = ModelToComponentFactory()
    return {
        path: (endpoint, factory.create_component(getattr(models, definition["type"]), definition, CONFIG))
        for path, definition, endpoint in requester_handlers(manifest)
    }


def test_manifest_uses_only_single_error_handlers(manifest: Mapping[str, Any]) -> None:
    definitions = {path: definition for path, definition, _ in requester_handlers(manifest)}
    assert definitions
    assert {path: handler["type"] for path, handler in definitions.items() if handler["type"] != "DefaultErrorHandler"} == {}


@pytest.mark.parametrize("status_code", [200, 400, 401, 402, 403, 404, 408, 410, 415, 429, 500, 501, 502, 503, 504])
def test_response_classification(handlers: Mapping[str, tuple[str, DefaultErrorHandler]], status_code: int) -> None:
    request = HttpRequest(url=f"{BASE_URL}/tickets")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body='{"description":"mock failure"}', status_code=status_code))
        response = requests.get(f"{BASE_URL}/tickets")

    default = DefaultErrorHandler(config=CONFIG, parameters={}).interpret_response(response)
    for path, (endpoint, handler) in handlers.items():
        resolution = handler.interpret_response(response)
        is_requested_items = endpoint.endswith("/requested_items")
        expected_action = default.response_action
        expected_message = default.error_message
        if status_code == 403 or (is_requested_items and status_code == 404):
            expected_action = ResponseAction.IGNORE
        elif is_requested_items and status_code == 429:
            expected_action = ResponseAction.RETRY
        if is_requested_items and status_code == 404:
            expected_message = "No data collected"
        assert resolution.response_action == expected_action, path
        assert resolution.failure_type == default.failure_type, path
        assert resolution.error_message == expected_message, path
        assert handler.max_retries == 5, path
        assert handler.max_time == 600, path


@pytest.mark.parametrize("status_code", [429, 500])
@pytest.mark.parametrize("retry_after", [None, "9"])
def test_retry_after_backoff(handlers: Mapping[str, tuple[str, DefaultErrorHandler]], status_code: int, retry_after: str | None) -> None:
    headers = {"Retry-After": retry_after} if retry_after else {}
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(url=f"{BASE_URL}/tickets"), HttpResponse(body="{}", status_code=status_code, headers=headers))
        response = requests.get(f"{BASE_URL}/tickets")

    for path, (endpoint, handler) in handlers.items():
        is_requested_items = endpoint.endswith("/requested_items")
        strategies = handler.backoff_strategies or []
        assert len(strategies) == (1 if is_requested_items else 0), path
        if strategies:
            assert strategies[0].backoff_time(response, attempt_count=0) == (9 if retry_after else None), path


@pytest.mark.parametrize(
    "stream_name,status_code", [("tickets", 403), ("requested_items", 403), ("requested_items", 404), ("requested_items", 429)]
)
def test_read_with_error_response(manifest_path: Path, monkeypatch: pytest.MonkeyPatch, stream_name: str, status_code: int) -> None:
    slept: list[float] = []
    monkeypatch.setattr("time.sleep", slept.append)
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG, catalog=catalog)
    tickets_request = HttpRequest(url=f"{BASE_URL}/tickets", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        if stream_name == "requested_items":
            http_mocker.get(
                tickets_request,
                HttpResponse(body=json.dumps({"tickets": [{"id": 1, "updated_at": "2024-01-02T00:00:00Z"}]})),
            )
            error_request = HttpRequest(url=f"{BASE_URL}/tickets/1/requested_items", query_params=ANY_QUERY_PARAMS)
        else:
            error_request = tickets_request
        error_response = HttpResponse(body="{}", status_code=status_code, headers={"Retry-After": "9"})
        if status_code == 429:
            http_mocker.get(error_request, [error_response, HttpResponse(body='{"requested_items": [{"id": 2}]}')])
        else:
            http_mocker.get(error_request, error_response)

        output = read(source, CONFIG, catalog)

        assert not output.errors
        records = []
        for message in output.records:
            assert message.record is not None
            records.append(message.record.data)
        assert records == ([{"id": 2}] if status_code == 429 else [])
        http_mocker.assert_number_of_calls(error_request, 2 if status_code == 429 else 1)
        assert [delay for delay in slept if delay] == ([10] if status_code == 429 else [])
