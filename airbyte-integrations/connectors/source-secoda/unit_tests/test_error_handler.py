# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {"api_key": "test-api-key"}
_STREAM_PATHS = {
    "tables": "/table/tables/",
    "terms": "/dictionary/terms/",
    "collections": "/collection/collections/",
}
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "http_codes": [500],
            "action": "FAIL",
        }
    ],
}
_RECORD = {"id": "record-1", "name": "Record 1"}


def _request(stream_name: str) -> HttpRequest:
    return HttpRequest(f"https://api.secoda.co{_STREAM_PATHS[stream_name]}", body="page_size=1")


def _success_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"results": [_RECORD], "links": {"next": None}}), status_code=200)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def test_error_handlers_are_single_default_error_handler() -> None:
    manifest = yaml.safe_load(Path(_YAML_FILE_PATH).read_text())
    stream_definitions = list(manifest["definitions"]["streams"].values()) + manifest["streams"]

    assert len(stream_definitions) == 6
    for stream in stream_definitions:
        assert stream["retriever"]["requester"]["error_handler"] == _EXPECTED_ERROR_HANDLER, stream["name"]


@pytest.mark.parametrize("stream_name", list(_STREAM_PATHS))
def test_successful_read(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request(stream_name), _success_response())

        output = _read(stream_name)

        assert [record.record.data for record in output.records] == [_RECORD]
        assert output.errors == []


@pytest.mark.parametrize("stream_name", list(_STREAM_PATHS))
@patch("time.sleep", lambda _: None)
def test_500_fails_without_retry(stream_name: str) -> None:
    request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body="", status_code=500))

        output = _read(stream_name, expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", list(_STREAM_PATHS))
@patch("time.sleep", lambda _: None)
def test_429_is_retried_then_succeeds(stream_name: str) -> None:
    request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [HttpResponse(body="", status_code=429), _success_response()],
        )

        output = _read(stream_name)

        assert [record.record.data for record in output.records] == [_RECORD]
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 2)
