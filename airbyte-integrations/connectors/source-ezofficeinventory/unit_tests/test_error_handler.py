# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Tests for the per-stream requester error handlers.

Every stream retries 429 responses as RATE_LIMITED, waiting on the
`Retry-After` header with a 60 second floor. Other statuses fall back to the
CDK default mapping.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "members"
_CONFIG = {"api_key": "test-api-key", "subdomain": "testcompany", "start_date": "2024-01-01T00:00:00Z"}
_URL_BASE = f"https://{_CONFIG['subdomain']}.ezofficeinventory.com"
_MAX_RETRIES = 5


def _stream_definitions() -> Dict[str, Any]:
    with open(_YAML_FILE_PATH) as manifest_file:
        return yaml.safe_load(manifest_file)["definitions"]["streams"]


_MEMBERS_PAGE_1_REQUEST = HttpRequest(
    f"{_URL_BASE}/members.api",
    query_params={"include_custom_fields": "true", "page": "1"},
    headers={"token": _CONFIG["api_key"]},
)


def _members_response(member_ids: List[int]) -> HttpResponse:
    members = [{"id": member_id, "email": f"member{member_id}@example.com"} for member_id in member_ids]
    return HttpResponse(body=json.dumps({"members": members}), status_code=200)


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


@pytest.mark.parametrize("stream_name", sorted(_stream_definitions()))
def test_stream_uses_default_error_handler_directly(stream_name: str) -> None:
    error_handler = _stream_definitions()[stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["backoff_strategies"] == [{"type": "WaitUntilTimeFromHeader", "header": "Retry-After", "min_wait": 60}]
    assert error_handler["response_filters"] == [
        {
            "type": "HttpResponseFilter",
            "action": "RATE_LIMITED",
            "http_codes": [429],
            "error_message": "Too many calls to the API - Rate Limit Hit",
        }
    ]


@patch("time.sleep", lambda _: None)
class TestMembersErrorHandler(TestCase):
    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _MEMBERS_PAGE_1_REQUEST,
            [HttpResponse(body="", status_code=429, headers={"Retry-After": "1"}), _members_response([1, 2])],
        )

        output = _read()

        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_MEMBERS_PAGE_1_REQUEST, 2)

    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _MEMBERS_PAGE_1_REQUEST,
            [HttpResponse(body="", status_code=500), HttpResponse(body="", status_code=503), _members_response([1])],
        )

        output = _read()

        assert [record.record.data["id"] for record in output.records] == [1]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_MEMBERS_PAGE_1_REQUEST, 3)

    @HttpMocker()
    def test_persistent_429_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_MEMBERS_PAGE_1_REQUEST, HttpResponse(body="", status_code=429, headers={"Retry-After": "1"}))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_MEMBERS_PAGE_1_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_MEMBERS_PAGE_1_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_MEMBERS_PAGE_1_REQUEST, 1)
