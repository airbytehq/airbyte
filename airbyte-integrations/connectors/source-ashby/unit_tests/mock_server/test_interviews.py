# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for the `interviews` stream on `source-ashby`."""

import json
import logging
from typing import Any, Dict, List
from unittest import TestCase

from jsonschema import Draft7Validator, FormatChecker
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "interviews"
_REMOVED_FIELDS = {
    "applicationId",
    "interviewScheduleId",
    "interviewStageId",
    "status",
    "createdAt",
    "updatedAt",
    "cancelledAt",
    "startTime",
    "endTime",
    "feedbackLink",
    "interviewerUserIds",
    "meetingLink",
}


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"success": True, "results": records, "moreDataAvailable": False}), status_code=200)


def _interviews_request() -> HttpRequest:
    return (
        AshbyRequestBuilder.endpoint("/interview.list")
        .with_api_key("test-api-key")
        .with_body_field("includeNonSharedInterviews", True)
        .with_body_field("includeArchived", True)
        .with_limit(100)
        .build()
    )


class TestInterviews(TestCase):
    @HttpMocker()
    def test_schema_matches_interview_definition_fields(self, http_mocker: HttpMocker):
        config = ConfigBuilder().build()
        source = get_source(config=config)
        catalog = source.discover(logging.getLogger("airbyte"), config)
        schema = {stream.name: stream for stream in catalog.streams}[_STREAM_NAME].json_schema
        properties = schema["properties"]
        record = {
            "id": "interview-1",
            "title": "Phone Screen",
            "externalTitle": "Phone Screen",
            "type": "Interview",
            "isArchived": False,
            "isDebrief": False,
            "isFeedbackRequired": True,
            "isFeedbackRequested": False,
            "instructionsHtml": "<p>Discuss experience.</p>",
            "instructionsPlain": "Discuss experience.",
            "jobId": "job-1",
            "feedbackFormDefinitionId": "form-1",
        }

        http_mocker.post(_interviews_request(), _page([record]))
        read_output = read(
            source,
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
            state=StateBuilder().build(),
        )

        assert read_output.errors == []
        emitted_record = read_output.records[0].record.data
        assert _REMOVED_FIELDS.isdisjoint(properties)
        assert "jobId" in properties
        assert set(emitted_record).issubset(properties)
        errors = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(emitted_record))
        assert errors == []
