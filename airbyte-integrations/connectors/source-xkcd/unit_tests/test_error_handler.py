# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `xkcd` stream error handler.

Pagination walks `{num + 1}/info.0.json` until xkcd answers 404 past the latest
comic, so the 404 IGNORE filter is what ends a sync cleanly. Every other status
falls back to the CDK default mapping, with retries bounded by `max_retries`.
"""

import json
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "xkcd"
_URL_BASE = "https://xkcd.com"
_CONFIG = {"comic_number": "1"}
_MAX_RETRIES = 5


_COMIC_1_REQUEST = HttpRequest(f"{_URL_BASE}/1/info.0.json")
_COMIC_2_REQUEST = HttpRequest(f"{_URL_BASE}/2/info.0.json")
_COMIC_3_REQUEST = HttpRequest(f"{_URL_BASE}/3/info.0.json")


def _comic(num: int) -> Dict[str, Any]:
    return {
        "num": num,
        "title": f"Comic {num}",
        "safe_title": f"Comic {num}",
        "alt": "",
        "img": f"https://imgs.xkcd.com/comics/{num}.png",
        "link": "",
        "news": "",
        "transcript": "",
        "day": "1",
        "month": "1",
        "year": "2006",
    }


def _comic_response(num: int) -> HttpResponse:
    return HttpResponse(body=json.dumps(_comic(num)), status_code=200)


def _not_found_response() -> HttpResponse:
    return HttpResponse(body="<html><body><h1>404 Not Found</h1></body></html>", status_code=404)


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


@patch("time.sleep", lambda _: None)
class TestXkcdErrorHandler(TestCase):
    @HttpMocker()
    def test_404_past_latest_comic_is_ignored_and_ends_sync(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_COMIC_1_REQUEST, _comic_response(1))
        http_mocker.get(_COMIC_2_REQUEST, _comic_response(2))
        http_mocker.get(_COMIC_3_REQUEST, _not_found_response())

        output = _read()

        assert [record.record.data["num"] for record in output.records] == [1, 2]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_COMIC_3_REQUEST, 1)

    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _COMIC_1_REQUEST,
            [HttpResponse(body="", status_code=500), HttpResponse(body="", status_code=503), _comic_response(1)],
        )
        http_mocker.get(_COMIC_2_REQUEST, _not_found_response())

        output = _read()

        assert [record.record.data["num"] for record in output.records] == [1]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_COMIC_1_REQUEST, 3)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_COMIC_1_REQUEST, [HttpResponse(body="", status_code=429), _comic_response(1)])
        http_mocker.get(_COMIC_2_REQUEST, _not_found_response())

        output = _read()

        assert [record.record.data["num"] for record in output.records] == [1]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_COMIC_1_REQUEST, 2)

    @HttpMocker()
    def test_persistent_5xx_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_COMIC_1_REQUEST, HttpResponse(body="", status_code=500))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_COMIC_1_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_COMIC_1_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_COMIC_1_REQUEST, 1)
