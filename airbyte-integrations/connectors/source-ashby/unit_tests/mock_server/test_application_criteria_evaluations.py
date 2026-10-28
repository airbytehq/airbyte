# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `application_criteria_evaluations` stream on `source-ashby`.

`POST /application.listCriteriaEvaluations` paginates with `cursor`/`limit` in the
JSON body and is partitioned per application by a filtered `application.list`
parent (only `PreInterviewScreen` applications that are not Archived or Hired).
The tests assert the exact request bodies sent for the parent page and each
child page.
"""

import json
import logging
from typing import Any, Dict, List
from unittest import TestCase

from jsonschema import Draft7Validator, FormatChecker
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "application_criteria_evaluations"
_CREATED_AFTER_MS = 1704067200000  # timestamp("2024-01-01T00:00:00Z") * 1000


def _application_record(application_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": application_id,
        "status": "Active",
        "currentInterviewStage": {"type": "PreInterviewScreen"},
    }
    record.update(overrides)
    return record


def _evaluation_record(record_id: str, **overrides) -> Dict[str, Any]:
    """An `ApplicationCriteriaEvaluation`, shaped like the success example in Ashby's `application.listCriteriaEvaluations` reference."""
    record = {
        "id": record_id,
        "criterion": {
            "id": "criterion-1",
            "title": "Location",
            "type": "ResumePrompt",
            "prompt": "Evaluate if the candidate's location aligns with the job requirements.",
            "applicationFormDefinitionId": None,
            "applicationFormFieldPath": None,
        },
        "status": "Completed",
        "outcome": "Meets",
        "reasoning": "The candidate's location aligns with the job's location requirement.",
        "skipReason": None,
        "outcomeNumber": 0.85,
        "evaluatedAt": "2024-06-01T12:00:00.000Z",
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


def _applications_first_page_request() -> HttpRequest:
    return (
        AshbyRequestBuilder.endpoint("/application.list")
        .with_api_key("test-api-key")
        .with_body_field("createdAfter", _CREATED_AFTER_MS)
        .with_limit(100)
        .build()
    )


def _evaluations_request(application_id: str, cursor: str = None) -> HttpRequest:
    builder = (
        AshbyRequestBuilder.endpoint("/application.listCriteriaEvaluations")
        .with_api_key("test-api-key")
        .with_body_field("applicationId", application_id)
        .with_limit(100)
    )
    if cursor is not None:
        builder = builder.with_cursor(cursor)
    return builder.build()


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestApplicationCriteriaEvaluations(TestCase):
    @HttpMocker()
    def test_reads_all_pages_for_each_parent_application(self, http_mocker: HttpMocker):
        """Every page of every qualifying application is read; filtered applications get no request."""
        applications_page = _applications_first_page_request()
        app1_page1 = _evaluations_request("app-1")
        app1_page2 = _evaluations_request("app-1", cursor="c2")
        app2_page1 = _evaluations_request("app-2")
        # app-3 is filtered out of the parent stream; any request for it raises NoMockAddress.
        http_mocker.post(
            applications_page,
            _page(
                [
                    _application_record("app-1"),
                    _application_record("app-2"),
                    _application_record("app-3", status="Hired"),
                ]
            ),
        )
        http_mocker.post(
            app1_page1,
            _page([_evaluation_record("eval-1"), _evaluation_record("eval-2")], next_cursor="c2"),
        )
        # The last page still carries a cursor; only `moreDataAvailable: false` may end pagination.
        http_mocker.post(app1_page2, _page([_evaluation_record("eval-3")], next_cursor="c3", more_data_available=False))
        http_mocker.post(app2_page1, _page([_evaluation_record("eval-4")]))

        output = _read()

        assert output.errors == []
        records_by_application = {}
        for message in output.records:
            records_by_application.setdefault(message.record.data["application_id"], set()).add(message.record.data["id"])
        assert records_by_application == {
            "app-1": {"eval-1", "eval-2", "eval-3"},
            "app-2": {"eval-4"},
        }
        http_mocker.assert_number_of_calls(applications_page, 1)
        http_mocker.assert_number_of_calls(app1_page1, 1)
        http_mocker.assert_number_of_calls(app1_page2, 1)
        http_mocker.assert_number_of_calls(app2_page1, 1)

    @HttpMocker()
    def test_discovered_primary_key_and_schema_match_emitted_evaluation(self, http_mocker: HttpMocker):
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        stream = {stream.name: stream for stream in catalog.streams}[_STREAM_NAME]
        schema = stream.json_schema

        assert stream.source_defined_primary_key == [["application_id"], ["id"]]
        assert {"assessmentType", "criterionName", "jobId"}.isdisjoint(schema["properties"])

        http_mocker.post(_applications_first_page_request(), _page([_application_record("app-1")]))
        http_mocker.post(_evaluations_request("app-1"), _page([_evaluation_record("eval-1")]))

        output = _read()

        assert output.errors == []
        record = output.records[0].record.data
        assert set(record).issubset(schema["properties"])
        errors = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(record))
        assert errors == []
