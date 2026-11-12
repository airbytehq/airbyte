# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import patch

import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "historical_news"
_REQUEST = HttpRequest(
    url="https://newsdata.io/api/1/archive",
    query_params={
        "apikey": "test_key",
        "from_date": "2024-01-01",
        "to_date": "2024-01-02",
    },
)
_CONFIG = {
    "api_key": "test_key",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-02",
}
_ARTICLE_BODY = {
    "status": "success",
    "results": [{"article_id": "a1", "pubDate": "2024-01-01 10:00:00", "title": "t"}],
    "nextPage": None,
}
_MAX_RETRIES = 5


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def _article_response() -> HttpResponse:
    return HttpResponse(body=json.dumps(_ARTICLE_BODY), status_code=200)


@patch("time.sleep", lambda _: None)
class TestNewsDataIOErrorHandler(TestCase):
    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        assert "Only Available for Premium Users" in str(output.errors)
        http_mocker.assert_number_of_calls(_REQUEST, 1)

    @HttpMocker()
    def test_429_honors_retry_after_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _REQUEST,
            [
                HttpResponse(body="", status_code=429, headers={"Retry-After": "1"}),
                _article_response(),
            ],
        )

        output = _read()

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_REQUEST, 2)

    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REQUEST, [HttpResponse(body="", status_code=500), _article_response()])

        output = _read()

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_REQUEST, 2)

    @HttpMocker()
    def test_persistent_5xx_stops_after_default_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REQUEST, HttpResponse(body="", status_code=500))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_REQUEST, _MAX_RETRIES + 1)

    def test_historical_news_uses_single_default_error_handler(self) -> None:
        manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
        error_handler = manifest["definitions"]["streams"][_STREAM_NAME]["retriever"]["requester"]["error_handler"]

        assert error_handler["type"] == "DefaultErrorHandler"
        assert error_handler["backoff_strategies"] == [
            {"type": "WaitTimeFromHeader", "header": "Retry-After", "max_waiting_time_in_seconds": 3600}
        ]
        assert error_handler["response_filters"] == [
            {
                "type": "HttpResponseFilter",
                "action": "FAIL",
                "http_codes": [403],
                "error_message": "Only Available for Premium Users. You don't have permission to access this resource.",
            },
            {
                "type": "HttpResponseFilter",
                "action": "RATE_LIMITED",
                "http_codes": [429],
                "error_message": "NewsData.io rate limit reached for your plan. Waiting for the limit to reset before retrying.",
            },
        ]
