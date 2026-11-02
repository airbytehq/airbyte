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


_STREAM_NAME = "accounts"
_URL_BASE = "https://mailtrap.io/api/"
_CONFIG = {"api_token": "test-token"}
_MAX_RETRIES = 2
_STREAM_NAMES = ("accounts", "billing_usage", "resources", "sending_domains", "inboxes", "messages", "projects")
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "max_retries": 2,
    "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 5}],
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "RATE_LIMITED",
            "http_codes": [429],
            "error_message": "Rate limit hit",
        }
    ],
}

_ACCOUNTS_REQUEST = HttpRequest(f"{_URL_BASE}accounts")
_BILLING_USAGE_REQUEST = HttpRequest(f"{_URL_BASE}accounts/1/billing/usage")


def _account_response() -> HttpResponse:
    body = [{"id": 1, "name": "a", "access_levels": [1000]}]
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestMailtrapErrorHandler(TestCase):
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
        for stream_name in _STREAM_NAMES:
            error_handler = streams[stream_name]["retriever"]["requester"]["error_handler"]
            assert error_handler == _EXPECTED_ERROR_HANDLER

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _ACCOUNTS_REQUEST,
            [HttpResponse(body="", status_code=429), _account_response()],
        )

        output = _read(_STREAM_NAME)

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ACCOUNTS_REQUEST, 2)

    @HttpMocker()
    def test_persistent_429_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ACCOUNTS_REQUEST, HttpResponse(body="", status_code=429))

        output = _read(_STREAM_NAME, expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_ACCOUNTS_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_500_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _ACCOUNTS_REQUEST,
            [HttpResponse(body="", status_code=500), _account_response()],
        )

        output = _read(_STREAM_NAME)

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ACCOUNTS_REQUEST, 2)

    @HttpMocker()
    def test_401_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ACCOUNTS_REQUEST, HttpResponse(body="", status_code=401))

        output = _read(_STREAM_NAME, expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_ACCOUNTS_REQUEST, 1)

    @HttpMocker()
    def test_billing_usage_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ACCOUNTS_REQUEST, _account_response())
        http_mocker.get(
            _BILLING_USAGE_REQUEST,
            [
                HttpResponse(body="", status_code=429),
                HttpResponse(body=json.dumps({"usage": 1}), status_code=200),
            ],
        )

        output = _read("billing_usage")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_BILLING_USAGE_REQUEST, 2)
