# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `interviewer_pools` stream on `source-ashby`.

`POST /interviewerPool.list` paginates with `cursor` and `limit` in the JSON body and
includes archived pools and archived training stages only when asked to.
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


_STREAM_NAME = "interviewer_pools"
_PATH = "/interviewerPool.list"


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
        "title": "Backend Interviewers",
        "isArchived": False,
        "trainingPath": {
            "id": "path-1",
            "enabled": True,
            "trainingStages": [
                {
                    "id": "training-stage-1",
                    "interviewerRole": "Shadow",
                    "interviewsRequired": 2,
                    "isArchived": False,
                    "approvalRequired": True,
                    "approvers": [
                        {
                            "id": "user-1",
                            "firstName": "Ana",
                            "lastName": "Example",
                            "email": "ana@example.com",
                            "globalRole": "Organization Admin",
                            "isEnabled": True,
                            "updatedAt": "2024-02-01T00:00:00.000Z",
                        }
                    ],
                }
            ],
        },
    }
    record.update(overrides)
    return record


def _request(cursor: str = None) -> HttpRequest:
    builder = (
        AshbyRequestBuilder.endpoint(_PATH)
        .with_api_key("test-api-key")
        .with_body_field("includeArchivedPools", True)
        .with_body_field("includeArchivedTrainingStages", True)
        .with_limit(100)
    )
    if cursor is not None:
        builder = builder.with_cursor(cursor)
    return builder.build()


class TestInterviewerPools(TestCase):
    @HttpMocker()
    def test_reads_all_pages_with_exact_request_bodies(self, http_mocker: HttpMocker):
        """Each page is a POST whose JSON body is exactly `includeArchivedPools`, `includeArchivedTrainingStages`, `limit`, and the returned cursor."""
        first_page = _request()
        second_page = _request(cursor="cursor-2")
        http_mocker.post(first_page, _page([_record("pool-1"), _record("pool-2")], next_cursor="cursor-2"))
        # The last page still carries a cursor; only `moreDataAvailable: false` may end pagination.
        http_mocker.post(second_page, _page([_record("pool-3")], next_cursor="cursor-3", more_data_available=False))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["pool-1", "pool-2", "pool-3"]
        assert output.records[0].record.data == _record("pool-1")
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_success_false_response_fails_sync_with_ashby_message(self, http_mocker: HttpMocker):
        """An HTTP 200 `success: false` error fails the sync instead of syncing empty."""
        message = "hiringProcessMetadataRead permission is required"
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

    def test_discover_nests_user_fields_under_training_stage_approvers(self):
        """Approver user fields are declared on `approvers[]` items, not on the parent `trainingStages[]` items."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        stream = next(stream for stream in catalog.streams if stream.name == _STREAM_NAME)

        training_stage = stream.json_schema["properties"]["trainingPath"]["properties"]["trainingStages"]["items"]
        approver = training_stage["properties"]["approvers"]["items"]

        assert {"id", "firstName", "lastName", "email", "globalRole", "isEnabled", "updatedAt", "managerId", "customFields"} <= set(
            approver["properties"]
        )
        assert approver["properties"]["updatedAt"]["format"] == "date-time"
        assert not {"firstName", "lastName", "email", "globalRole", "managerId", "customFields"} & set(training_stage["properties"])
