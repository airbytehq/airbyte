# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG: Mapping[str, Any] = {
    "credentials": {"auth_type": "AccessToken", "access_token": "test_token"},
    "start_date": "2024-01-01T00:00:00Z",
}
BASE_URL = "https://tasks.googleapis.com/tasks/v1/"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _manifest() -> dict[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _error_handler(stream: str):
    manifest = _manifest()
    definition = next(item for item in manifest["streams"] if item["name"] == stream)["retriever"]["requester"]["error_handler"]
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", f"{BASE_URL}users/@me/lists").prepare()
    response.url = response.request.url
    response.headers["Content-Type"] = "application/json"
    response._content = b"{}"
    return response


def _request(path: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}{path}",
        query_params=ANY_QUERY_PARAMS,
        headers={"Authorization": "Bearer test_token"},
    )


def _assert_default_max_results(http_mocker: HttpMocker, path: str) -> None:
    requests_for_path = [request for request in http_mocker._mocker.request_history if urlparse(request.url).path.endswith(path)]
    assert requests_for_path
    for request in requests_for_path:
        assert parse_qs(urlparse(request.url).query)["maxResults"] == ["50"]


def _response_body(status_code: int, body: dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _read_stream(stream: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    config = {**CONFIG, "records_limit": "50"}
    return read(get_source(config), config, catalog, expecting_exception=expecting_exception)


def _item(item_id: str) -> dict[str, str]:
    return {
        "id": item_id,
        "title": "Test item",
        "updated": "2024-01-02T00:00:00.000000Z",
    }


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _manifest()
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "CompositeErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not composite_handlers


@pytest.mark.parametrize("stream", ["tasks", "lists_tasks"])
def test_stream_error_handler_retries_rate_limits(stream: str) -> None:
    handler = _error_handler(stream)

    assert handler.max_retries == 5

    rate_limited = handler.interpret_response(_response(429))
    assert rate_limited.response_action == ResponseAction.RATE_LIMITED
    assert "Rate limit hit" in rate_limited.error_message

    success = handler.interpret_response(_response(200))
    assert success.response_action == ResponseAction.SUCCESS

    strategy = handler.backoff_strategies[0]
    assert [strategy.backoff_time(response_or_exception=None, attempt_count=attempt_count) for attempt_count in (1, 2, 3)] == [4, 8, 16]


def test_tasks_retries_rate_limit_then_returns_record() -> None:
    tasks_request = _request("users/@me/lists")
    with HttpMocker() as http_mocker:
        http_mocker.get(
            tasks_request,
            [
                _response_body(429, {"error": {"code": 429, "message": "Rate limit hit"}}),
                _response_body(200, {"items": [_item("list-1")]}),
            ],
        )

        output = _read_stream("tasks")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["list-1"]
        http_mocker.assert_number_of_calls(tasks_request, 2)
        _assert_default_max_results(http_mocker, "users/@me/lists")


def test_lists_tasks_retries_rate_limit_then_returns_record() -> None:
    task_lists_request = _request("users/@me/lists")
    child_tasks_request = _request("lists/list-1/tasks")
    with HttpMocker() as http_mocker:
        http_mocker.get(task_lists_request, _response_body(200, {"items": [_item("list-1")]}))
        http_mocker.get(
            child_tasks_request,
            [
                _response_body(429, {"error": {"code": 429, "message": "Rate limit hit"}}),
                _response_body(200, {"items": [_item("task-1")]}),
            ],
        )

        output = _read_stream("lists_tasks")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["task-1"]
        http_mocker.assert_number_of_calls(child_tasks_request, 2)
        _assert_default_max_results(http_mocker, "lists/list-1/tasks")


def test_tasks_rate_limit_exhaustion_emits_error_after_max_retries() -> None:
    tasks_request = _request("users/@me/lists")
    with HttpMocker() as http_mocker:
        http_mocker.get(tasks_request, _response_body(429, {"error": {"code": 429, "message": "Rate limit hit"}}))

        output = _read_stream("tasks", expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(tasks_request, 6)
