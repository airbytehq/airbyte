# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `interview_plans` stream on `source-ashby`.

`POST /interviewPlan.list` paginates with `cursor` and `limit` in the JSON body and
returns archived plans only when `includeArchived` is true. The same stream
definition is the parent of `interview_stages`.
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


_STREAM_NAME = "interview_plans"
_PATH = "/interviewPlan.list"


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
        "title": "Engineering Interview Plan",
        "isArchived": False,
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-02-01T00:00:00.000Z",
    }
    record.update(overrides)
    return record


def _request(cursor: str = None) -> HttpRequest:
    builder = AshbyRequestBuilder.endpoint(_PATH).with_api_key("test-api-key").with_body_field("includeArchived", True).with_limit(100)
    if cursor is not None:
        builder = builder.with_cursor(cursor)
    return builder.build()


class TestInterviewPlans(TestCase):
    @HttpMocker()
    def test_reads_all_pages_with_exact_request_bodies(self, http_mocker: HttpMocker):
        """Each page is a POST whose JSON body is exactly `includeArchived`, `limit`, and the returned cursor."""
        first_page = _request()
        second_page = _request(cursor="cursor-2")
        http_mocker.post(first_page, _page([_record("plan-1"), _record("plan-2")], next_cursor="cursor-2"))
        # The last page still carries a cursor; only `moreDataAvailable: false` may end pagination.
        http_mocker.post(second_page, _page([_record("plan-3")], next_cursor="cursor-3", more_data_available=False))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["plan-1", "plan-2", "plan-3"]
        assert output.records[0].record.data == _record("plan-1")
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_success_false_response_fails_sync_with_ashby_message(self, http_mocker: HttpMocker):
        """An HTTP 200 `success: false` error fails the sync instead of syncing empty."""
        message = "interviewsRead permission is required"
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

    @HttpMocker()
    def test_interview_stages_reuses_interview_plans_as_parent(self, http_mocker: HttpMocker):
        """`interview_stages` partitions on the same `interview_plans` requests, not a second copy."""
        plans_request = _request()
        http_mocker.post(plans_request, _page([_record("plan-1")]))
        stages_request = (
            AshbyRequestBuilder.interview_stages_endpoint()
            .with_api_key("test-api-key")
            .with_body_field("interviewPlanId", "plan-1")
            .build()
        )
        http_mocker.post(stages_request, _page([{"id": "stage-1", "interviewPlanId": "plan-1"}]))
        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream("interview_stages", SyncMode.full_refresh).build()

        output = read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["stage-1"]
        http_mocker.assert_number_of_calls(plans_request, 1)
        http_mocker.assert_number_of_calls(stages_request, 1)
