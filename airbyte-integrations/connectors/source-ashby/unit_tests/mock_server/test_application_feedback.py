# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `application_feedback` stream on `source-ashby`.

`POST /applicationFeedback.list` paginates with `cursor` and `limit` in the JSON body, and
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


_STREAM_NAME = "application_feedback"
_CREATED_AFTER_MS = 1704067200000  # 2024-01-01T00:00:00Z in epoch milliseconds


def _feedback_record(record_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": record_id,
        "applicationId": "app-1",
        "applicationHistoryId": "hist-1",
        "feedbackFormDefinitionId": "form-def-1",
        "interviewId": "interview-1",
        "interviewEventId": "event-1",
        "submittedAt": "2024-06-01T12:00:00Z",
        "submittedByUser": {
            "id": "user-1",
            "firstName": "Ana",
            "lastName": "Example",
            "email": "ana@example.com",
            "globalRole": "Organization Admin",
            "isEnabled": True,
            "updatedAt": "2024-05-01T00:00:00Z",
        },
        "creditedToUser": {
            "id": "user-2",
            "firstName": "Bob",
            "lastName": "Example",
            "email": "bob@example.com",
            "globalRole": "Interviewer",
            "isEnabled": True,
            "updatedAt": "2024-05-01T00:00:00Z",
        },
        "formDefinition": {
            "sections": [
                {
                    "title": "Scorecard",
                    "fields": [
                        {
                            "isRequired": True,
                            "field": {
                                "id": "field-1",
                                "type": "ValueSingleSelect",
                                "path": "overall_recommendation",
                                "title": "Overall recommendation",
                                "humanReadablePath": "Scorecard / Overall recommendation",
                                "isNullable": False,
                                "selectableValues": [
                                    {"label": "Hire", "value": "hire"},
                                    {"label": "No Hire", "value": "no_hire"},
                                ],
                            },
                        }
                    ],
                }
            ]
        },
        "submittedValues": {"overall_recommendation": "hire", "technical_skills": 4},
    }
    record.update(overrides)
    return record


def _page(records: List[Dict[str, Any]], next_cursor: str = None) -> HttpResponse:
    body = {
        "success": True,
        "results": records,
        "moreDataAvailable": next_cursor is not None,
        "syncToken": "tok",
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    return HttpResponse(body=json.dumps(body), status_code=200)


def _first_page_request() -> HttpRequest:
    return (
        AshbyRequestBuilder.application_feedback_endpoint()
        .with_api_key("test-api-key")
        .with_created_after(_CREATED_AFTER_MS)
        .with_limit(100)
        .build()
    )


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestApplicationFeedback(TestCase):
    @HttpMocker()
    def test_reads_all_pages_with_exact_request_bodies(self, http_mocker: HttpMocker):
        """Each page is a POST whose JSON body is exactly `createdAfter`, `limit`, and the returned cursor."""
        first_page = _first_page_request()
        second_page = (
            AshbyRequestBuilder.application_feedback_endpoint()
            .with_api_key("test-api-key")
            .with_created_after(_CREATED_AFTER_MS)
            .with_limit(100)
            .with_cursor("cursor-2")
            .build()
        )
        http_mocker.post(first_page, _page([_feedback_record("fb-1"), _feedback_record("fb-2")], next_cursor="cursor-2"))
        third_record = _feedback_record("fb-3")
        del third_record["creditedToUser"]
        http_mocker.post(second_page, _page([third_record]))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["fb-1", "fb-2", "fb-3"]
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_record_keeps_submitted_values_verbatim(self, http_mocker: HttpMocker):
        """Free-form `submittedValues` and the submitted `formDefinition` pass through untouched."""
        http_mocker.post(_first_page_request(), _page([_feedback_record("fb-1")]))

        output = _read()

        assert output.errors == []
        record = output.records[0].record.data
        assert record["submittedValues"] == {"overall_recommendation": "hire", "technical_skills": 4}
        assert record["formDefinition"]["sections"][0]["fields"][0]["field"]["selectableValues"][0] == {
            "label": "Hire",
            "value": "hire",
        }

    def test_discover_declares_application_feedback_stream(self):
        """Discovery declares the stream with `id` primary key, full_refresh only, and a loose `submittedValues`."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}
        stream = streams_by_name[_STREAM_NAME]

        assert stream.source_defined_primary_key == [["id"]]
        assert stream.supported_sync_modes == [SyncMode.full_refresh]
        submitted_values = stream.json_schema["properties"]["submittedValues"]
        assert submitted_values["additionalProperties"] is True
        assert "properties" not in submitted_values
