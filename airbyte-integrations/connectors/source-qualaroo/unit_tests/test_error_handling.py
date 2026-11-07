# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from collections.abc import Iterator
from typing import Any

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.qualaroo.com/api/v1"
_CONFIG = {
    "key": "k",
    "token": "t",
    "start_date": "2021-03-01T00:00:00.000Z",
    "survey_ids": [],
}
_START_DATE = "1614556800"
_SURVEY_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/nudges",
    query_params={"limit": "500", "start_date": _START_DATE},
)
_RESPONSE_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/nudges/1/responses.json",
    query_params={"limit": "500", "start_date": _START_DATE},
)
_STREAM_NAMES = ("surveys", "responses")


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda *_args, **_kwargs: None)


def _walk(node: Any) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _target_request(stream_name: str) -> HttpRequest:
    return _SURVEY_REQUEST if stream_name == "surveys" else _RESPONSE_REQUEST


def _mock_parent_survey(http_mocker: HttpMocker, stream_name: str) -> None:
    if stream_name == "responses":
        http_mocker.get(_SURVEY_REQUEST, HttpResponse(json.dumps([{"id": 1}]), status_code=200))


def _read_stream(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(_CONFIG),
        config=_CONFIG,
        catalog=catalog,
        expecting_exception=expecting_exception,
    )


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    nodes = list(_walk(manifest))

    assert not any(node.get("type") == "CompositeErrorHandler" for node in nodes)

    for stream_name in _STREAM_NAMES:
        stream = manifest["definitions"]["streams"][stream_name]
        error_handler = stream["retriever"]["requester"]["error_handler"]
        assert error_handler["type"] == "DefaultErrorHandler"
        assert "response_filters" not in error_handler


@pytest.mark.parametrize(
    ("stream_name", "status_code"),
    [(stream_name, status_code) for stream_name in _STREAM_NAMES for status_code in (500, 502, 503, 504)],
)
def test_server_errors_retry_and_emit_the_next_page(stream_name: str, status_code: int) -> None:
    target_request = _target_request(stream_name)
    with HttpMocker() as http_mocker:
        _mock_parent_survey(http_mocker, stream_name)
        http_mocker.get(
            target_request,
            [
                HttpResponse('{"error": "server error"}', status_code=status_code),
                HttpResponse(json.dumps([{"id": 10}]), status_code=200),
            ],
        )

        output = _read_stream(stream_name)

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(target_request, 2)


@pytest.mark.parametrize(
    ("stream_name", "status_code"),
    [(stream_name, status_code) for stream_name in _STREAM_NAMES for status_code in (500, 504)],
)
def test_persistent_server_errors_exhaust_retries(stream_name: str, status_code: int) -> None:
    target_request = _target_request(stream_name)
    with HttpMocker() as http_mocker:
        _mock_parent_survey(http_mocker, stream_name)
        http_mocker.get(target_request, HttpResponse('{"error": "server error"}', status_code=status_code))

        output = _read_stream(stream_name, expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.transient_error
        assert output.records == []
        http_mocker.assert_number_of_calls(target_request, 6)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_rate_limit_retries_once(stream_name: str) -> None:
    target_request = _target_request(stream_name)
    with HttpMocker() as http_mocker:
        _mock_parent_survey(http_mocker, stream_name)
        http_mocker.get(
            target_request,
            [
                HttpResponse('{"error": "rate limited"}', status_code=429),
                HttpResponse(json.dumps([{"id": 10}]), status_code=200),
            ],
        )

        output = _read_stream(stream_name)

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(target_request, 2)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_unauthorized_response_fails_as_config_error(stream_name: str) -> None:
    target_request = _target_request(stream_name)
    with HttpMocker() as http_mocker:
        _mock_parent_survey(http_mocker, stream_name)
        http_mocker.get(target_request, HttpResponse('{"error": "unauthorized"}', status_code=401))

        output = _read_stream(stream_name, expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        http_mocker.assert_number_of_calls(target_request, 1)
