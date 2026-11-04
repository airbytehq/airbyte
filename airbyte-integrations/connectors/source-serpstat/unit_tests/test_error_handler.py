# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.jinja import _ENVIRONMENT
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_URL = "https://api.serpstat.com/v4/"
_CONFIG = {
    "api_key": "test-key",
    "domain": "serpstat.com",
    "domains": ["serpstat.com"],
    "region_id": "g_us",
    "page_size": 10,
    "pages_to_fetch": 1,
}
_FIXED_NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)
_REQUEST_ID = str(_FIXED_NOW)
_DOMAIN_HISTORY_REQUEST = HttpRequest(
    _URL,
    body={
        "id": _REQUEST_ID,
        "method": "SerpstatDomainProcedure.getDomainsHistory",
        "params": {
            "se": "g_us",
            "page": 1,
            "size": 10,
            "sort": {"date": "desc"},
            "domain": "serpstat.com",
            "during_all_time": True,
        },
    },
)
_DOMAINS_SUMMARY_REQUEST = HttpRequest(
    _URL,
    body={
        "id": _REQUEST_ID,
        "method": "SerpstatDomainProcedure.getDomainsInfo",
        "params": {"se": "g_us", "domains": ["serpstat.com"]},
    },
)
_MAX_RETRIES = 5


def _response(body: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=200)


def _api_error(code: int, message: str) -> HttpResponse:
    return _response({"id": "1", "error": {"code": code, "message": message}})


def _success() -> HttpResponse:
    return _response(
        {
            "id": "1",
            "result": {
                "data": [{"domain": "serpstat.com", "date": "2025-01-01"}],
                "summary_info": {"page": 1},
            },
        }
    )


def _read_stream(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        config=_CONFIG,
        catalog=catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
@patch.dict(_ENVIRONMENT.globals, {"now_utc": lambda: _FIXED_NOW})
class TestSerpstatErrorHandler(TestCase):
    @HttpMocker()
    def test_domain_history_retries_json_rpc_error_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(_DOMAIN_HISTORY_REQUEST, [_api_error(32000, "Too Many Requests"), _success()])

        output = _read_stream("Domain history")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_DOMAIN_HISTORY_REQUEST, 2)

    @HttpMocker()
    def test_domain_history_persistent_json_rpc_error_fails_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(_DOMAIN_HISTORY_REQUEST, _api_error(32000, "Too Many Requests"))

        output = _read_stream("Domain history", expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(_DOMAIN_HISTORY_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_domains_summary_invalid_token_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(_DOMAINS_SUMMARY_REQUEST, _api_error(401, "Invalid token"))

        output = _read_stream("Domains summary", expecting_exception=True)

        assert output.errors
        assert output.is_in_logs("Invalid Token")
        http_mocker.assert_number_of_calls(_DOMAINS_SUMMARY_REQUEST, 1)

    @HttpMocker()
    def test_domains_summary_retries_rate_limit_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(_DOMAINS_SUMMARY_REQUEST, [_api_error(429, "Too Many Requests"), _success()])

        output = _read_stream("Domains summary")

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(_DOMAINS_SUMMARY_REQUEST, 2)
