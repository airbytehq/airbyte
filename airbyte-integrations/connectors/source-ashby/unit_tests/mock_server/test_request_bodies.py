# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests asserting the exact first-page request bodies `source-ashby`
sends for the streams that accept `includeArchived` / `includeDeactivated`.
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


# stream name -> (API path, expected extra first-page body fields)
_STREAMS_WITH_ARCHIVED = {
    "archive_reasons": ("/archiveReason.list", {"includeArchived": True}),
    "candidate_tags": ("/candidateTag.list", {"includeArchived": True}),
    "custom_fields": ("/customField.list", {"includeArchived": True}),
    "departments": ("/department.list", {"includeArchived": True}),
    "feedback_form_definitions": ("/feedbackFormDefinition.list", {"includeArchived": True}),
    "interviews": ("/interview.list", {"includeNonSharedInterviews": True, "includeArchived": True}),
    "locations": ("/location.list", {"includeArchived": True}),
    "sources": ("/source.list", {"includeArchived": True}),
    "users": ("/user.list", {"includeDeactivated": True}),
}


def _empty_page() -> HttpResponse:
    return HttpResponse(body=json.dumps({"success": True, "results": [], "moreDataAvailable": False}), status_code=200)


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestRequestBodies(TestCase):
    def _run_stream_case(self, http_mocker: HttpMocker, stream_name: str):
        path, body_fields = _STREAMS_WITH_ARCHIVED[stream_name]
        builder = AshbyRequestBuilder.endpoint(path).with_api_key("test-api-key").with_limit(100)
        for key, value in body_fields.items():
            builder = builder.with_body_field(key, value)
        request = builder.build()
        http_mocker.post(request, _empty_page())

        output = _read(stream_name)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_first_page_bodies(self, http_mocker: HttpMocker):
        for stream_name in _STREAMS_WITH_ARCHIVED:
            with self.subTest(stream=stream_name):
                self._run_stream_case(http_mocker, stream_name)

    def test_discover_declares_new_fields_and_spec_text(self):
        """Discovery exposes the newly declared fields and the updated start_date description."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}

        assert "brandId" in streams_by_name["applications"].json_schema["properties"]["job"]["properties"]
        assert "referenceIdentifier" in streams_by_name["candidates"].json_schema["properties"]["customFields"]["items"]["properties"]
        for field in ("isDateOnlyField", "isEditableOnlyViaPublicApi", "referenceIdentifier", "referencedObjectType"):
            assert field in streams_by_name["custom_fields"].json_schema["properties"]

        interview_event = streams_by_name["interview_schedules"].json_schema["properties"]["interviewEvents"]["items"]["properties"]
        assert interview_event["extraData"]["additionalProperties"] is True
        interviewer = interview_event["interviewers"]["items"]["properties"]
        assert interviewer["updatedAt"]["format"] == "date-time"
        assert interviewer["isFeedbackRequired"]["type"] == ["null", "boolean"]

        assert "locationExternalName" in streams_by_name["job_postings"].json_schema["properties"]

        spec = get_source(config=config).spec(logging.getLogger("airbyte"))
        assert spec.connectionSpecification["properties"]["start_date"]["description"] == (
            "Only applications, application feedback, and interview schedules "
            "created on or after this date are replicated, and application history "
            "and application criteria evaluations are read only for those "
            "applications. All other streams are read in full on every sync. "
            "Format: 2017-01-25T00:00:00Z."
        )
