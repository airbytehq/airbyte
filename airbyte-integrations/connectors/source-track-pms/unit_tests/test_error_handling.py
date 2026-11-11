# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Iterator, Mapping

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source

import airbyte_cdk.sources.declarative.models.declarative_component_schema as declarative_component_schema
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"customer_domain": "example.trackhs.com", "api_key": "key", "api_secret": "secret"}
IGNORE_404_STREAMS = {"units_daily_pricing_v2", "units_types_daily_pricing_v2"}
RESOLVED_MANIFEST = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
STREAMS_BY_NAME = {stream["name"]: stream for stream in RESOLVED_MANIFEST["streams"]}
STREAM_NAMES = sorted(STREAMS_BY_NAME)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _walk(node: Any) -> Iterator[Any]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def test_manifest_has_no_composite_error_handler() -> None:
    composite_type = "Composite" + "ErrorHandler"
    assert not [node for node in _walk(RESOLVED_MANIFEST) if node.get("type") == composite_type]


def _build_error_handler(stream_name: str) -> ErrorHandler:
    model = STREAMS_BY_NAME[stream_name]["retriever"]["requester"]["error_handler"]
    model_type = {
        "Composite" + "ErrorHandler": getattr(declarative_component_schema, "Composite" + "ErrorHandler"),
        "DefaultErrorHandler": DefaultErrorHandlerModel,
    }[model["type"]]
    return ModelToComponentFactory().create_component(model_type, model, config=CONFIG, parameters={})


def _response(body: Mapping[str, Any]) -> requests.Response:
    response = requests.Response()
    response.status_code = body["status"]
    response._content = json.dumps(body).encode()
    response.headers["Content-Type"] = "application/json"
    return response


@pytest.mark.parametrize("stream_name", STREAM_NAMES, ids=STREAM_NAMES)
def test_stream_error_handler_behavior(stream_name: str) -> None:
    handler = _build_error_handler(stream_name)

    invalid_page = handler.interpret_response(_response({"status": 409, "detail": "Invalid page provided"}))
    assert invalid_page.response_action == ResponseAction.IGNORE
    assert "Track's inappropriate 409" in invalid_page.error_message

    rate_limited_response = _response({"status": 429})
    rate_limited = handler.interpret_response(rate_limited_response)
    assert rate_limited.response_action == ResponseAction.RATE_LIMITED
    assert "Track rate limit" in rate_limited.error_message
    backoff_handler = handler
    handler_type = STREAMS_BY_NAME[stream_name]["retriever"]["requester"]["error_handler"]["type"]
    if handler_type == "Composite" + "ErrorHandler":
        backoff_handler = handler.error_handlers[-1]
    assert backoff_handler.backoff_time(rate_limited_response, attempt_count=1) == 305

    not_found = handler.interpret_response(_response({"status": 404}))
    if stream_name in IGNORE_404_STREAMS:
        assert not_found.response_action == ResponseAction.IGNORE
        assert "Track's 404" in not_found.error_message
    else:
        assert not_found.response_action == ResponseAction.FAIL

    assert handler.max_retries == 5


def _tags_request(page: int | None = None) -> HttpRequest:
    query_params = {"size": "100"}
    if page is not None:
        query_params["page"] = str(page)
    return HttpRequest(
        url="https://example.trackhs.com/api/tags",
        query_params=query_params,
    )


def _http_response(body: Mapping[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(body),
        status_code=status_code,
        headers={"Content-Type": "application/json"},
    )


def _read_tags() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("tags", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog)


def test_tags_read_ignores_invalid_page_after_records() -> None:
    records = [{"id": record_id} for record_id in range(100)]
    with HttpMocker() as http_mocker:
        first_page = _tags_request()
        second_page = _tags_request(2)
        http_mocker.get(first_page, _http_response({"_embedded": {"tags": records}}))
        http_mocker.get(
            second_page,
            _http_response({"status": 409, "detail": "Invalid page provided"}, status_code=409),
        )

        output = _read_tags()

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == list(range(100))
    http_mocker.assert_number_of_calls(first_page, 1)
    http_mocker.assert_number_of_calls(second_page, 1)


def test_tags_read_retries_rate_limit_and_records_wait(no_sleep) -> None:
    records = [{"id": record_id} for record_id in range(3)]
    request = _tags_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [
                _http_response({"status": 429}, status_code=429),
                _http_response({"_embedded": {"tags": records}}),
            ],
        )

        output = _read_tags()

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == list(range(3))
    assert any(duration >= 305 for duration in no_sleep)
    http_mocker.assert_number_of_calls(request, 2)
