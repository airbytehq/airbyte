# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from typing import Any, Iterator

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_STREAM_NAME = "projects"
_URL_BASE = "https://test-site.teamwork.com/projects/api/v3/"
_CONFIG = {
    "site_name": "test-site",
    "username": "test-user",
    "password": "test-password",
    "start_date": "2024-01-01T00:00:00Z",
}
_MAX_RETRIES = 3
_ERROR_MESSAGE = (
    "Teamwork rejected the request as unprocessable (HTTP 422). Check the connector configuration and retry; "
    "contact Airbyte support if the error persists."
)
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "max_retries": _MAX_RETRIES,
    "backoff_strategies": [
        {"type": "WaitUntilTimeFromHeader", "header": "X-Rate-Limit-Reset"},
        {"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 60},
    ],
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "FAIL",
            "http_codes": [422],
            "error_message": _ERROR_MESSAGE,
        }
    ],
}
_PROJECTS_REQUEST = HttpRequest(f"{_URL_BASE}projects.json", query_params=ANY_QUERY_PARAMS)
_NOTEBOOKS_REQUEST = HttpRequest(f"{_URL_BASE}notebooks.json", query_params=ANY_QUERY_PARAMS)
_NOTEBOOK_COMMENTS_REQUEST = HttpRequest(f"{_URL_BASE}notebooks/1/comments.json", query_params=ANY_QUERY_PARAMS)


@pytest.fixture(autouse=True)
def record_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: sleeps.append(seconds))
    return sleeps


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker


def _read(stream_name: str = _STREAM_NAME, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


def _project_response() -> HttpResponse:
    body = {"projects": [{"id": 1}], "meta": {"page": {"pageOffset": 0, "hasMore": False}}}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _error_message(output: EntrypointOutput) -> str:
    assert output.errors, output.get_formatted_error_message()
    return output.errors[0].trace.error.message or ""


def test_manifest_has_one_shared_default_error_handler() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            assert value.get("type") != "Composite" + "ErrorHandler"
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(manifest)
    assert manifest["definitions"]["base_requester"]["error_handler"] == _EXPECTED_ERROR_HANDLER
    for stream in manifest["definitions"]["streams"].values():
        assert "error_handler" not in stream["retriever"]["requester"]


def test_422_fails_after_one_call_with_the_configured_message(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    http_mocker.get(_PROJECTS_REQUEST, HttpResponse(body="unprocessable", status_code=422))

    output = _read(expecting_exception=True)

    assert output.records == []
    http_mocker.assert_number_of_calls(_PROJECTS_REQUEST, 1)
    assert "HTTP 422" in _error_message(output)
    assert record_sleeps == []


def test_429_waits_for_the_rate_limit_reset_then_succeeds(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    reset_at = int(time.time()) + 120
    http_mocker.get(
        _PROJECTS_REQUEST,
        [
            HttpResponse(
                body="rate limited",
                status_code=429,
                headers={"X-Rate-Limit-Reset": str(reset_at), "X-Rate-Limit-Remaining": "100"},
            ),
            _project_response(),
        ],
    )

    output = _read()

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(_PROJECTS_REQUEST, 2)
    backoff_sleeps = [seconds for seconds in record_sleeps if seconds]
    assert len(backoff_sleeps) == 1
    assert 110 <= backoff_sleeps[0] <= 125


def test_429_without_reset_header_uses_the_sixty_second_backoff(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    http_mocker.get(
        _PROJECTS_REQUEST,
        [
            HttpResponse(body="rate limited", status_code=429, headers={"X-Rate-Limit-Remaining": "100"}),
            _project_response(),
        ],
    )

    output = _read()

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(_PROJECTS_REQUEST, 2)
    assert [seconds for seconds in record_sleeps if seconds] == pytest.approx([61.0])


def test_persistent_429_stops_after_max_retries(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    http_mocker.get(
        _PROJECTS_REQUEST,
        HttpResponse(body="rate limited", status_code=429, headers={"X-Rate-Limit-Remaining": "100"}),
    )

    output = _read(expecting_exception=True)

    assert output.records == []
    assert output.errors
    http_mocker.assert_number_of_calls(_PROJECTS_REQUEST, _MAX_RETRIES + 1)
    assert [seconds for seconds in record_sleeps if seconds] == pytest.approx([61.0, 61.0, 61.0])


def test_500_is_retried_then_succeeds(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    http_mocker.get(_PROJECTS_REQUEST, [HttpResponse(body="server error", status_code=500), _project_response()])

    output = _read()

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(_PROJECTS_REQUEST, 2)
    assert [seconds for seconds in record_sleeps if seconds] == pytest.approx([61.0])


def test_401_fails_without_retry(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    http_mocker.get(_PROJECTS_REQUEST, HttpResponse(body="unauthorized", status_code=401))

    output = _read(expecting_exception=True)

    assert output.records == []
    assert output.errors
    http_mocker.assert_number_of_calls(_PROJECTS_REQUEST, 1)
    assert record_sleeps == []


def test_notebook_comment_422_fails_after_one_call(http_mocker: HttpMocker, record_sleeps: list[float]) -> None:
    notebook_body = {"notebooks": [{"id": 1}], "meta": {"page": {"pageOffset": 0, "hasMore": False}}}
    http_mocker.get(_NOTEBOOKS_REQUEST, HttpResponse(body=json.dumps(notebook_body), status_code=200))
    http_mocker.get(_NOTEBOOK_COMMENTS_REQUEST, HttpResponse(body="unprocessable", status_code=422))

    output = _read("notebooks_comments.json", expecting_exception=True)

    assert output.records == []
    http_mocker.assert_number_of_calls(_NOTEBOOK_COMMENTS_REQUEST, 1)
    assert "HTTP 422" in _error_message(output)
    assert record_sleeps == []
