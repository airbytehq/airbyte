# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for `source-ashby` error handling.

Ashby reports most errors as HTTP 200 responses with `success: false` and an
`errorInfo` object. The shared error handler must fail the sync with Ashby's
message, map permission and credential errors to `config_error`, retry on
HTTP 429/5xx, and let `application_history` and `application_criteria_evaluations`
skip `application_not_found` partitions.
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


_CREATED_AFTER_MS = 1704067200000  # timestamp("2024-01-01T00:00:00Z") * 1000
_PARENT_RECORD = {"id": "parent-1", "status": "Active", "currentInterviewStage": {"type": "PreInterviewScreen"}}

# (stream, calls the stream makes in order): every call but the last returns `_PARENT_RECORD`; the last returns the error.
# Substreams appear twice so both the parent's and the child's error handler are exercised.
_REQUESTER_CASES = [
    ("applications", [("/application.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100})]),
    ("application_feedback", [("/applicationFeedback.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100})]),
    ("archive_reasons", [("/archiveReason.list", {"includeArchived": True, "limit": 100})]),
    ("candidate_tags", [("/candidateTag.list", {"includeArchived": True, "limit": 100})]),
    ("candidates", [("/candidate.list", {"limit": 100})]),
    ("custom_fields", [("/customField.list", {"includeArchived": True, "limit": 100})]),
    ("departments", [("/department.list", {"includeArchived": True, "limit": 100})]),
    ("feedback_form_definitions", [("/feedbackFormDefinition.list", {"includeArchived": True, "limit": 100})]),
    ("interview_schedules", [("/interviewSchedule.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100})]),
    ("interviews", [("/interview.list", {"includeNonSharedInterviews": True, "includeArchived": True, "limit": 100})]),
    ("job_postings", [("/jobPosting.list", {"limit": 100})]),
    ("jobs", [("/job.list", {"limit": 100})]),
    ("locations", [("/location.list", {"includeArchived": True, "limit": 100})]),
    ("offers", [("/offer.list", {"limit": 100})]),
    ("sources", [("/source.list", {"includeArchived": True, "limit": 100})]),
    ("users", [("/user.list", {"includeDeactivated": True, "limit": 100})]),
    ("interview_stages", [("/interviewPlan.list", {"includeArchived": True, "limit": 100})]),
    (
        "interview_stages",
        [("/interviewPlan.list", {"includeArchived": True, "limit": 100}), ("/interviewStage.list", {"interviewPlanId": "parent-1"})],
    ),
    ("application_criteria_evaluations", [("/application.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100})]),
    (
        "application_criteria_evaluations",
        [
            ("/application.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100}),
            ("/application.listCriteriaEvaluations", {"applicationId": "parent-1", "limit": 100}),
        ],
    ),
    ("application_history", [("/application.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100})]),
    (
        "application_history",
        [
            ("/application.list", {"createdAfter": _CREATED_AFTER_MS, "limit": 100}),
            ("/application.listHistory", {"applicationId": "parent-1", "limit": 100}),
        ],
    ),
]


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
    def test_errors_only_envelope_keeps_ashbys_message(self, http_mocker: HttpMocker):
        """A `success: false` envelope with only `errors[]` still surfaces Ashby's message."""
        request = _request("/department.list", includeArchived=True, limit=100)
        body = {"success": False, "errors": [{"message": "Invalid limit", "parameter": "limit"}]}
        http_mocker.post(request, HttpResponse(body=json.dumps(body), status_code=200))

        output = _read("departments")

        assert output.errors != []
        assert "Invalid limit" in output.errors[0].trace.error.message

    @HttpMocker()
    def test_null_error_info_does_not_crash(self, http_mocker: HttpMocker):
        """A `success: false` envelope with `errorInfo: null` fails with a sensible message instead of a template error."""
        request = _request("/department.list", includeArchived=True, limit=100)
        body = {"success": False, "errors": None, "errorInfo": None}
        http_mocker.post(request, HttpResponse(body=json.dumps(body), status_code=200))

        output = _read("departments")

        assert output.errors != []
        assert "Ashby returned an error" in output.errors[0].trace.error.message
        assert "no message provided" in output.errors[0].trace.error.message

    @HttpMocker()
    def test_missing_endpoint_permission_is_config_error(self, http_mocker: HttpMocker):
        """`missing_endpoint_permission` fails as a config error with an actionable message."""
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, _error("missing_endpoint_permission", "API key does not have the required permission", status_code=403))

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
        """A 429 carrying Ashby's `success: false` envelope is retried, not failed by the generic `success: false` filter."""
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, [_error("rate_limited", "Too many requests", status_code=429), _page([{"id": "dept-1"}])])

        with mock.patch("time.sleep"):
            output = _read("departments")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["dept-1"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_5xx_is_retried(self, http_mocker: HttpMocker):
        """A 5xx carrying Ashby's `success: false` envelope is retried, not failed by the generic `success: false` filter."""
        request = _request("/department.list", includeArchived=True, limit=100)
        http_mocker.post(request, [_error("internal_error", "Internal server error", status_code=503), _page([{"id": "dept-1"}])])

        with mock.patch("time.sleep"):
            output = _read("departments")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["dept-1"]
        http_mocker.assert_number_of_calls(request, 2)

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

    @HttpMocker()
    def test_application_criteria_evaluations_skips_application_not_found(self, http_mocker: HttpMocker):
        """`application_criteria_evaluations` ignores `application_not_found` partitions instead of failing."""
        applications_request = _request("/application.list", createdAfter=1704067200000, limit=100)
        in_review = {"status": "Active", "currentInterviewStage": {"type": "PreInterviewScreen"}}
        http_mocker.post(applications_request, _page([{"id": "app-1", **in_review}, {"id": "app-2", **in_review}]))
        http_mocker.post(
            _request("/application.listCriteriaEvaluations", applicationId="app-1", limit=100),
            _error("application_not_found", "Application not found"),
        )
        http_mocker.post(
            _request("/application.listCriteriaEvaluations", applicationId="app-2", limit=100),
            _page([{"id": "eval-1", "status": "Completed", "outcome": "DefinitelyYes"}]),
        )

        output = _read("application_criteria_evaluations")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["eval-1"]
        assert {message.record.data["application_id"] for message in output.records} == {"app-2"}

    def test_every_requester_maps_missing_endpoint_permission_to_config_error(self):
        """Every requester, including each substream parent and `application_history`'s override, fails on HTTP 200 `success: false`."""
        for stream_name, calls in _REQUESTER_CASES:
            with self.subTest(stream=stream_name, failing_path=calls[-1][0]), HttpMocker() as http_mocker:
                for path, body in calls[:-1]:
                    http_mocker.post(_request(path, **body), _page([_PARENT_RECORD]))
                failing_path, failing_body = calls[-1]
                http_mocker.post(
                    _request(failing_path, **failing_body),
                    _error("missing_endpoint_permission", "API key does not have the required permission", status_code=403),
                )

                output = _read(stream_name)

                assert output.errors != []
                assert "lacks a module permission" in output.errors[0].trace.error.message
                assert output.errors[0].trace.error.failure_type == FailureType.config_error
