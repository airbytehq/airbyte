# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `job_templates` stream on `source-ashby`.

`POST /jobTemplate.list` paginates with `cursor` and `limit` in the JSON body.
"""

import json
import logging
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "job_templates"
_PATH = "/jobTemplate.list"


def _page(records: List[Dict[str, Any]], next_cursor: str = None, more_data_available: bool = None) -> HttpResponse:
    body = {
        "success": True,
        "results": records,
        "moreDataAvailable": next_cursor is not None if more_data_available is None else more_data_available,
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def _record(record_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": record_id,
        "title": "Software Engineer",
        "status": "Active",
        "locationId": "location-1",
        "departmentId": "department-1",
        "defaultInterviewPlanId": "plan-1",
        "interviewPlanIds": ["plan-1"],
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-02-01T00:00:00.000Z",
    }
    record.update(overrides)
    return record


def _request(cursor: str = None) -> HttpRequest:
    builder = AshbyRequestBuilder.endpoint(_PATH).with_api_key("test-api-key").with_limit(100)
    if cursor is not None:
        builder = builder.with_cursor(cursor)
    return builder.build()


class TestJobTemplates(TestCase):
    @HttpMocker()
    def test_reads_all_pages_with_exact_request_bodies(self, http_mocker: HttpMocker):
        """Each page is a POST whose JSON body is exactly `limit` and the returned cursor."""
        first_page = _request()
        second_page = _request(cursor="cursor-2")
        http_mocker.post(first_page, _page([_record("template-1"), _record("template-2")], next_cursor="cursor-2"))
        http_mocker.post(second_page, _page([_record("template-3")], next_cursor="cursor-3", more_data_available=False))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["template-1", "template-2", "template-3"]
        assert output.records[0].record.data == _record("template-1")
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_success_false_response_fails_sync_with_ashby_message(self, http_mocker: HttpMocker):
        """An HTTP 200 `success: false` error fails the sync instead of syncing empty."""
        message = "jobsRead permission is required"
        body = {
            "success": False,
            "errors": ["missing_endpoint_permission"],
            "errorInfo": {"code": "missing_endpoint_permission", "message": message, "requestId": "req-1"},
        }
        http_mocker.post(_request(), HttpResponse(body=json.dumps(body), status_code=200))

        output = _read()

        assert output.records == []
        assert any(message in error.trace.error.message for error in output.errors)

    def test_discover_declares_stream(self):
        """Discovery declares the stream with `id` primary key and full_refresh only."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}
        stream = streams_by_name[_STREAM_NAME]

        assert stream.source_defined_primary_key == [["id"]]
        assert stream.supported_sync_modes == [SyncMode.full_refresh]
