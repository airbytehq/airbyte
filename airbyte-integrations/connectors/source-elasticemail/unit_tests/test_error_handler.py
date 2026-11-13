# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "api_key": "test-api-key",
    "from": "2024-01-01T00:00:00Z",
    "scope_type": "Personal",
    "start_date": "2024-01-01T00:00:00Z",
}
_STATISTICS_REQUEST = HttpRequest(
    url="https://api.elasticemail.com/v4/statistics",
    query_params={"from": _CONFIG["from"], "limit": "100", "offset": "0"},
    headers={"X-ElasticEmail-ApiKey": _CONFIG["api_key"]},
)
_TEMPLATES_REQUEST = HttpRequest(
    url="https://api.elasticemail.com/v4/templates",
    query_params={"scopeType": _CONFIG["scope_type"], "limit": "100", "offset": "0"},
    headers={"X-ElasticEmail-ApiKey": _CONFIG["api_key"]},
)
_EXPECTED_ERROR_HANDLERS = {
    "statistics": {
        "type": "DefaultErrorHandler",
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "FAIL",
                "http_codes": [400],
                "error_message": 'Please enter " FROM "',
                "error_message_contains": "Missing required parameter - from",
            }
        ],
    },
    "templates": {
        "type": "DefaultErrorHandler",
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "FAIL",
                "http_codes": [400],
                "error_message": "Please enter scope type",
                "error_message_contains": "Missing required parameter - scopeType",
            }
        ],
    },
}


def _read_stream(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestElasticEmailErrorHandler(TestCase):
    def test_manifest_has_no_composite_error_handler(self) -> None:
        manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                assert value.get("type") != ("Composite" + "ErrorHandler")
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(manifest)
        streams = manifest["definitions"]["streams"]
        for stream_name, expected_error_handler in _EXPECTED_ERROR_HANDLERS.items():
            error_handler = streams[stream_name]["retriever"]["requester"]["error_handler"]
            assert error_handler == expected_error_handler

    @HttpMocker()
    def test_statistics_400_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _STATISTICS_REQUEST,
            HttpResponse(body="Missing required parameter - from", status_code=400),
        )

        output = _read_stream("statistics", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_STATISTICS_REQUEST, 1)

    @HttpMocker()
    def test_templates_400_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _TEMPLATES_REQUEST,
            HttpResponse(body="Missing required parameter - scopeType", status_code=400),
        )

        output = _read_stream("templates", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_TEMPLATES_REQUEST, 1)

    @HttpMocker()
    def test_statistics_500_retries_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _STATISTICS_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                HttpResponse(body=json.dumps([{"Name": "test"}]), status_code=200),
            ],
        )

        output = _read_stream("statistics")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_STATISTICS_REQUEST, 2)

    @HttpMocker()
    def test_templates_500_retries_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _TEMPLATES_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                HttpResponse(body=json.dumps([{"Name": "test"}]), status_code=200),
            ],
        )

        output = _read_stream("templates")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_TEMPLATES_REQUEST, 2)
