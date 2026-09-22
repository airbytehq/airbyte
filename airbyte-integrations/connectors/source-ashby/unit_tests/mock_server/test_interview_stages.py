# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `interview_stages` stream on `source-ashby`.

`POST /interviewStage.list` paginates with `cursor` and `limit` in the JSON body, and
the tests assert the exact request bodies the connector sends for each page.
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
        "isArchived": False,
    }
    record.update(overrides)
    return record


def _page(records: List[Dict[str, Any]], next_cursor: str = None) -> HttpResponse:
    body = {
        "success": True,
        "results": records,
        "moreDataAvailable": next_cursor is not None,
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    return HttpResponse(body=json.dumps(body), status_code=200)


def _first_page_request() -> HttpRequest:
    return AshbyRequestBuilder.interview_stages_endpoint().with_api_key("test-api-key").with_limit(100).build()


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestInterviewStages(TestCase):
    @HttpMocker()
    def test_reads_all_pages_with_exact_request_bodies(self, http_mocker: HttpMocker):
        """Each page is a POST whose JSON body is exactly `limit` and the returned cursor."""
        first_page = _first_page_request()
        second_page = (
            AshbyRequestBuilder.interview_stages_endpoint().with_api_key("test-api-key").with_limit(100).with_cursor("cursor-2").build()
        )
        http_mocker.post(first_page, _page([_stage_record("stage-1"), _stage_record("stage-2")], next_cursor="cursor-2"))
        http_mocker.post(second_page, _page([_stage_record("stage-3")]))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["stage-1", "stage-2", "stage-3"]
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    def test_discover_declares_interview_stages_stream(self):
        """Discovery declares the stream with `id` primary key and full_refresh only."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}
        stream = streams_by_name[_STREAM_NAME]

        assert stream.source_defined_primary_key == [["id"]]
        assert stream.supported_sync_modes == [SyncMode.full_refresh]
