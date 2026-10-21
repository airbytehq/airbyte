# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `interview_stages` stream on `source-ashby`.

`POST /interviewStage.list` requires an `interviewPlanId` in the request body and
returns every stage of that plan without pagination, so `interview_stages` is a
substream of `POST /interviewPlan.list` (which paginates with `cursor`/`limit`).
The tests assert the exact request bodies the connector sends for the parent
pages and for each partition's single child request.
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


_STREAM_NAME = "interview_stages"


def _stage_record(record_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": record_id,
        "title": "Technical Interview",
        "type": "Active",
        "orderInInterviewPlan": 2,
        "interviewPlanId": "plan-1",
        "interviewStageGroupId": "group-1",
    }
    record.update(overrides)
    return record


def _page(records: List[Dict[str, Any]], next_cursor: str = None, more_data_available: bool = None) -> HttpResponse:
    body = {
        "success": True,
        "results": records,
        "moreDataAvailable": next_cursor is not None if more_data_available is None else more_data_available,
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    return HttpResponse(body=json.dumps(body), status_code=200)


def _error_body(code: str, message: str) -> str:
    return json.dumps(
        {
            "success": False,
            "errors": [code],
            "errorInfo": {"code": code, "message": message, "requestId": "req-1"},
        }
    )


def _plans_first_page_request() -> HttpRequest:
    return (
        AshbyRequestBuilder.endpoint("/interviewPlan.list")
        .with_api_key("test-api-key")
        .with_body_field("includeArchived", True)
        .with_limit(100)
        .build()
    )


def _plans_second_page_request() -> HttpRequest:
    return (
        AshbyRequestBuilder.endpoint("/interviewPlan.list")
        .with_api_key("test-api-key")
        .with_body_field("includeArchived", True)
        .with_limit(100)
        .with_cursor("c2")
        .build()
    )


def _stages_request(plan_id: str) -> HttpRequest:
    return AshbyRequestBuilder.interview_stages_endpoint().with_api_key("test-api-key").with_body_field("interviewPlanId", plan_id).build()


def _mock_parent_pages(http_mocker: HttpMocker) -> List[HttpRequest]:
    plans_page1 = _plans_first_page_request()
    plans_page2 = _plans_second_page_request()
    http_mocker.post(
        plans_page1,
        _page([{"id": "plan-1", "isArchived": True}, {"id": "plan-2", "isArchived": False}], next_cursor="c2"),
    )
    # The last page still carries a cursor; only `moreDataAvailable: false` may end pagination.
    http_mocker.post(plans_page2, _page([{"id": "plan-3", "isArchived": False}], next_cursor="c3", more_data_available=False))
    return [plans_page1, plans_page2]


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestInterviewStages(TestCase):
    @HttpMocker()
    def test_reads_stages_for_every_interview_plan(self, http_mocker: HttpMocker):
        """The connector paginates `interviewPlan.list`, then calls `interviewStage.list` once per plan."""
        plans_requests = _mock_parent_pages(http_mocker)
        stages_requests = {}
        for plan_id, stage_ids in {"plan-1": ["stage-1", "stage-2"], "plan-2": ["stage-3"], "plan-3": ["stage-4"]}.items():
            stages_requests[plan_id] = _stages_request(plan_id)
            http_mocker.post(stages_requests[plan_id], _page([_stage_record(s, interviewPlanId=plan_id) for s in stage_ids]))

        output = _read()

        assert output.errors == []
        records_by_id = {message.record.data["id"]: message.record.data for message in output.records}
        assert set(records_by_id) == {"stage-1", "stage-2", "stage-3", "stage-4"}
        assert records_by_id["stage-1"]["interview_plan_is_archived"] is True
        assert records_by_id["stage-2"]["interview_plan_is_archived"] is True
        assert records_by_id["stage-3"]["interview_plan_is_archived"] is False
        assert records_by_id["stage-4"]["interview_plan_is_archived"] is False
        for request in plans_requests:
            http_mocker.assert_number_of_calls(request, 1)
        for request in stages_requests.values():
            http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_success_false_response_fails_sync_with_ashby_message(self, http_mocker: HttpMocker):
        """An HTTP 200 `success: false` error from `interviewStage.list` fails instead of syncing empty."""
        _mock_parent_pages(http_mocker)
        message = "interviewPlanId: Invalid input: expected string, received undefined"
        for plan_id in ("plan-1", "plan-2", "plan-3"):
            http_mocker.post(_stages_request(plan_id), HttpResponse(body=_error_body("invalid_input", message), status_code=200))

        output = _read()

        assert output.errors != []
        assert any(message in error.trace.error.message for error in output.errors)

    def test_discover_declares_interview_stages_stream(self):
        """Discovery declares the stream with `id` primary key and full_refresh only."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}
        stream = streams_by_name[_STREAM_NAME]

        assert stream.source_defined_primary_key == [["id"]]
        assert stream.supported_sync_modes == [SyncMode.full_refresh]
