# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_STREAM_NAME = "logs"
_CONFIG = {
    "api_key": "test_api_key",
    "application_key": "test_app_key",
    "site": "datadoghq.com",
    "query": "*",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-02T00:00:00Z",
}
_LOGS_REQUEST = HttpRequest(
    "https://api.datadoghq.com/api/v2/logs/events",
    query_params={
        "filter[query]": "*",
        "filter[from]": "2024-01-01T00:00:00Z",
        "filter[to]": "2024-01-02T00:00:00Z",
    },
)
_SUCCESS_BODY = {"data": [{"id": "log-1", "type": "log", "attributes": {}}], "links": {}, "meta": {}}


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def _success_response() -> HttpResponse:
    return HttpResponse(body=json.dumps(_SUCCESS_BODY), status_code=200)


@patch("time.sleep", lambda _: None)
class TestDatadogLogsErrorHandler(TestCase):
    def test_logs_error_handler_is_single_default_error_handler(self) -> None:
        manifest_text = _YAML_FILE_PATH.read_text()
        manifest = yaml.safe_load(manifest_text)
        error_handler = manifest["definitions"]["streams"]["logs"]["retriever"]["requester"]["error_handler"]

        assert error_handler["type"] == "DefaultErrorHandler"
        assert error_handler["max_retries"] == 3
        assert error_handler["backoff_strategies"] == [{"type": "ExponentialBackoffStrategy"}]
        assert any(
            response_filter.get("action") == "RETRY" and response_filter.get("http_codes") == [429]
            for response_filter in error_handler["response_filters"]
        )
        assert "CompositeErrorHandler" not in manifest_text

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_LOGS_REQUEST, [HttpResponse(body="", status_code=429), _success_response()])

        output = _read()

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_LOGS_REQUEST, 2)

    @HttpMocker()
    def test_persistent_429_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_LOGS_REQUEST, HttpResponse(body="", status_code=429))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_LOGS_REQUEST, 4)

    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_LOGS_REQUEST, [HttpResponse(body="", status_code=500), _success_response()])

        output = _read()

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_LOGS_REQUEST, 2)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_LOGS_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_LOGS_REQUEST, 1)
