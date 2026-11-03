# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {
    "credentials": {"auth_type": "access_token", "access_token": "test"},
    "start_date": "2021-01-01T00:00:00Z",
}
_STREAM_NAMES = ("forms", "responses", "webhooks", "workspaces", "images", "themes")
_ERROR_MESSAGE = (
    "Could not complete the stream: Source Typeform has been waiting for too long for a response from Typeform API. "
    "Please try again later."
)
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "response_filters": [
        {
            "http_codes": [499],
            "action": "FAIL",
            "error_message": _ERROR_MESSAGE,
        }
    ],
}
_WORKSPACES_REQUEST = HttpRequest(
    "https://api.typeform.com/workspaces",
    query_params={"page_size": "200"},
)


def _read_workspaces(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("workspaces", SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestTypeformErrorHandler(TestCase):
    def test_manifest_has_no_composite_error_handler(self) -> None:
        manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
        composite_error_handler_type = "".join(("Composite", "ErrorHandler"))

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                assert value.get("type") != composite_error_handler_type
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(manifest)

        error_handlers = {"trim_forms_stream": manifest["definitions"]["trim_forms_stream"]["retriever"]["requester"]["error_handler"]}
        error_handlers.update(
            {
                stream["name"]: stream["retriever"]["requester"]["error_handler"]
                for stream in manifest["streams"]
                if stream["name"] in _STREAM_NAMES
            }
        )
        assert error_handlers == {
            "trim_forms_stream": _EXPECTED_ERROR_HANDLER,
            **{stream_name: _EXPECTED_ERROR_HANDLER for stream_name in _STREAM_NAMES},
        }

    @HttpMocker()
    def test_499_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_WORKSPACES_REQUEST, HttpResponse(body="", status_code=499))

        output = _read_workspaces(expecting_exception=True)

        assert output.records == []
        assert output.errors
        assert output.is_in_logs("499") or any("499" in str(error) for error in output.errors)
        http_mocker.assert_number_of_calls(_WORKSPACES_REQUEST, 1)

    @HttpMocker()
    def test_500_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _WORKSPACES_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                HttpResponse(body=json.dumps({"items": []}), status_code=200),
            ],
        )

        output = _read_workspaces()

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_WORKSPACES_REQUEST, 2)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _WORKSPACES_REQUEST,
            [
                HttpResponse(body="", status_code=429),
                HttpResponse(body=json.dumps({"items": []}), status_code=200),
            ],
        )

        output = _read_workspaces()

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_WORKSPACES_REQUEST, 2)

    @HttpMocker()
    def test_401_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_WORKSPACES_REQUEST, HttpResponse(body="", status_code=401))

        output = _read_workspaces(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_WORKSPACES_REQUEST, 1)
