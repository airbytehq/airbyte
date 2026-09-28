# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for `source-ashby` error handling.

Ashby reports most errors as HTTP 200 responses with `success: false` and an
`errorInfo` object. The shared error handler must fail the sync with Ashby's
message, map permission and credential errors to `config_error`, retry on
HTTP 429/5xx, and let `application_history` skip `application_not_found`
partitions.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase, mock

from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


def _page(records: List[Dict[str, Any]], next_cursor: str = None) -> HttpResponse:
    body = {
        "success": True,
        "results": records,
        "moreDataAvailable": next_cursor is not None,
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    return HttpResponse(body=json.dumps(body), status_code=200)


def _error(code: str, message: str, status_code: int = 200) -> HttpResponse:
    body = {
        "success": False,
        "errors": [code],
        "errorInfo": {"code": code, "message": message, "requestId": "req-1"},
    }
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _request(path: str, **body_fields: Any) -> HttpRequest:
    builder = AshbyRequestBuilder.endpoint(path).with_api_key("test-api-key")
    for key, value in body_fields.items():
        builder = builder.with_body_field(key, value)
    return builder.build()


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestErrorHandling(TestCase):
    @HttpMocker()
    def test_success_false_fails_sync_with_ashby_message(self, http_mocker: HttpMocker):
        """An HTTP 200 `success: false` response fails the sync with Ashby's error message."""
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, _error("cursor_invalid", "Invalid cursor 'abc'"))

        output = _read("departments")

        assert output.errors != []
        assert "Invalid cursor" in output.errors[0].trace.error.message
        assert output.errors[0].trace.error.failure_type == FailureType.system_error

    @HttpMocker()
    def test_missing_endpoint_permission_is_config_error(self, http_mocker: HttpMocker):
        """`missing_endpoint_permission` fails as a config error with an actionable message."""
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, _error("missing_endpoint_permission", "API key does not have the required permission"))

        output = _read("departments")

        assert output.errors != []
        assert "lacks a module permission" in output.errors[0].trace.error.message
        assert output.errors[0].trace.error.failure_type == FailureType.config_error

    @HttpMocker()
    def test_401_is_config_error(self, http_mocker: HttpMocker):
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, HttpResponse(body="Unauthorized", status_code=401))

        output = _read("departments")

        assert output.errors != []
        assert "HTTP 401" in output.errors[0].trace.error.message
        assert output.errors[0].trace.error.failure_type == FailureType.config_error

    @HttpMocker()
    def test_403_is_config_error(self, http_mocker: HttpMocker):
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, HttpResponse(body="Forbidden", status_code=403))

        output = _read("departments")

        assert output.errors != []
        assert output.errors[0].trace.error.failure_type == FailureType.config_error

    @HttpMocker()
    def test_429_is_retried(self, http_mocker: HttpMocker):
        """A 429 response is retried and the following page's records are read."""
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, [HttpResponse(body="Rate limited", status_code=429), _page([{"id": "dept-1"}])])

        with mock.patch("time.sleep"):
            output = _read("departments")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["dept-1"]

    @HttpMocker()
    def test_application_history_skips_application_not_found(self, http_mocker: HttpMocker):
        """`application_history` ignores `application_not_found` partitions instead of failing."""
        applications_request = _request("/application.list", createdAfter=1704067200000, limit=100)
        http_mocker.post(applications_request, _page([{"id": "app-1"}, {"id": "app-2"}]))
        http_mocker.post(
            _request("/application.listHistory", applicationId="app-1", limit=100),
            _error("application_not_found", "Application not found"),
        )
        http_mocker.post(
            _request("/application.listHistory", applicationId="app-2", limit=100),
            _page([{"id": "history-1", "stageId": "stage-1", "title": "Lead", "enteredStageAt": "2024-01-01T00:00:00Z"}]),
        )

        output = _read("application_history")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["history-1"]
        assert {message.record.data["application_id"] for message in output.records} == {"app-2"}
