# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for sync-token incremental sync on every Ashby stream whose endpoint accepts `syncToken`."""

import json
import logging
from typing import Any, Dict, List, Optional

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_CREATED_AFTER = 1704067200000  # ConfigBuilder's default start_date, 2024-01-01T00:00:00Z, in epoch ms.

# (stream name, endpoint, fixed request body fields, advertised cursor field)
_SYNC_TOKEN_STREAMS = [
    ("application_feedback", "/applicationFeedback.list", {"createdAfter": _CREATED_AFTER}, None),
    ("approvals", "/approval.list", {}, None),
    ("candidate_tags", "/candidateTag.list", {"includeArchived": True}, None),
    ("candidates", "/candidate.list", {}, "updatedAt"),
    ("custom_fields", "/customField.list", {"includeArchived": True}, None),
    ("departments", "/department.list", {"includeArchived": True}, "updatedAt"),
    ("feedback_form_definitions", "/feedbackFormDefinition.list", {"includeArchived": True}, None),
    ("interview_plans", "/interviewPlan.list", {"includeArchived": True}, "updatedAt"),
    ("interview_schedules", "/interviewSchedule.list", {"createdAfter": _CREATED_AFTER}, "updatedAt"),
    ("interviewer_pools", "/interviewerPool.list", {"includeArchivedPools": True, "includeArchivedTrainingStages": True}, None),
    ("interviews", "/interview.list", {"includeNonSharedInterviews": True, "includeArchived": True}, None),
    ("job_templates", "/jobTemplate.list", {}, None),
    ("jobs", "/job.list", {}, "updatedAt"),
    ("locations", "/location.list", {"includeArchived": True}, None),
    ("offers", "/offer.list", {}, None),
    ("openings", "/opening.list", {}, None),
    ("projects", "/project.list", {}, None),
    ("source_tracking_links", "/sourceTrackingLink.list", {"includeDisabled": True}, None),
    ("survey_form_definitions", "/surveyFormDefinition.list", {}, None),
    ("users", "/user.list", {"includeDeactivated": True}, "updatedAt"),
]

# Endpoints whose request schema has no syncToken: these streams must stay full refresh.
_FULL_REFRESH_STREAMS = [
    "application_criteria_evaluations",
    "archive_reasons",
    "interview_stage_groups",
    "interview_stages",
    "job_boards",
    "job_postings",
    "sources",
]

_STREAM_IDS = [stream[0] for stream in _SYNC_TOKEN_STREAMS]


def _page(
    records: List[Dict[str, Any]],
    *,
    more_data_available: bool,
    next_cursor: Optional[str] = None,
    sync_token: Optional[str] = None,
) -> HttpResponse:
    body: Dict[str, Any] = {"success": True, "results": records, "moreDataAvailable": more_data_available}
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    if sync_token is not None:
        body["syncToken"] = sync_token
    return HttpResponse(body=json.dumps(body), status_code=200)


def _request(path: str, body: Dict[str, Any], cursor: Optional[str] = None, sync_token: Optional[str] = None) -> HttpRequest:
    builder = AshbyRequestBuilder.endpoint(path).with_api_key("test-api-key").with_limit(100)
    for key, value in body.items():
        builder = builder.with_body_field(key, value)
    if cursor is not None:
        builder = builder.with_cursor(cursor)
    if sync_token is not None:
        builder = builder.with_body_field("syncToken", sync_token)
    return builder.build()


def _token_state(stream_name: str, token: str):
    return (
        StateBuilder()
        .with_stream_state(stream_name, {"state_type": "sync_token", "token": token, "committed_at": "2026-10-01T00:00:00Z"})
        .build()
    )


def _read(stream_name: str, state=None) -> EntrypointOutput:
    config = ConfigBuilder().build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


def _emitted_tokens(output: EntrypointOutput) -> List[Any]:
    return [
        message.state.stream.stream_state.__dict__.get("token")
        for message in output.state_messages
        if message.state and message.state.stream and message.state.stream.stream_state
    ]


@pytest.mark.parametrize("stream_name,path,body,cursor_field", _SYNC_TOKEN_STREAMS, ids=_STREAM_IDS)
def test_first_sync_pages_without_a_token_and_commits_the_terminal_token(stream_name, path, body, cursor_field):
    first_page = _request(path, body)
    second_page = _request(path, body, cursor="c1")
    with HttpMocker() as http_mocker:
        http_mocker.post(first_page, _page([{"id": "r1"}], more_data_available=True, next_cursor="c1"))
        http_mocker.post(second_page, _page([{"id": "r2"}], more_data_available=False, sync_token="tok1"))

        output = _read(stream_name)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["r1", "r2"]
    stream_state = output.most_recent_state.stream_state.__dict__
    assert stream_state["state_type"] == "sync_token"
    assert stream_state["token"] == "tok1"
    http_mocker.assert_number_of_calls(first_page, 1)
    http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize("stream_name,path,body,cursor_field", _SYNC_TOKEN_STREAMS, ids=_STREAM_IDS)
def test_incremental_sync_sends_the_stored_token_on_every_page(stream_name, path, body, cursor_field):
    first_page = _request(path, body, sync_token="tok0")
    second_page = _request(path, body, cursor="c1", sync_token="tok0")
    with HttpMocker() as http_mocker:
        http_mocker.post(first_page, _page([{"id": "r1"}], more_data_available=True, next_cursor="c1", sync_token="tok0"))
        http_mocker.post(second_page, _page([{"id": "r2"}], more_data_available=False, sync_token="tok2"))

        output = _read(stream_name, _token_state(stream_name, "tok0"))

    assert output.errors == []
    assert len(output.records) == 2
    assert output.most_recent_state.stream_state.__dict__["token"] == "tok2"
    http_mocker.assert_number_of_calls(first_page, 1)
    http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize(
    "error_body,expected_instruction",
    [
        (
            {"success": False, "errors": [{"code": "incremental_sync_too_large", "message": "Too many pages"}]},
            "Switch this stream to Full Refresh",
        ),
        ({"success": False, "errors": ["incremental_sync_too_large"]}, "Switch this stream to Full Refresh"),
        ({"success": False, "errors": ["sync_token_expired"]}, "Refresh this stream"),
        ({"success": False, "errorInfo": {"code": "sync_token_invalid", "message": "Token invalid"}}, "Refresh this stream"),
    ],
    ids=["incremental_sync_too_large", "incremental_sync_too_large_string", "sync_token_expired", "sync_token_invalid"],
)
@pytest.mark.parametrize(
    "stream_name,path,body,cursor_field",
    [stream for stream in _SYNC_TOKEN_STREAMS if stream[0] in ("users", "interview_schedules")],
    ids=["interview_schedules", "users"],
)
def test_rejected_token_fails_the_stream_and_keeps_the_stored_token(
    stream_name, path, body, cursor_field, error_body, expected_instruction
):
    first_page = _request(path, body, sync_token="tok_old")
    second_page = _request(path, body, cursor="c1", sync_token="tok_old")
    with HttpMocker() as http_mocker:
        http_mocker.post(first_page, _page([{"id": "r1"}], more_data_available=True, next_cursor="c1", sync_token="tok_old"))
        http_mocker.post(second_page, HttpResponse(body=json.dumps(error_body), status_code=200))

        output = _read(stream_name, _token_state(stream_name, "tok_old"))

    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert expected_instruction in error.message
    assert all(token == "tok_old" for token in _emitted_tokens(output))
    http_mocker.assert_number_of_calls(first_page, 1)
    http_mocker.assert_number_of_calls(second_page, 1)


def test_discovery_advertises_incremental_only_for_sync_token_streams():
    config = ConfigBuilder().build()
    catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
    streams_by_name = {stream.name: stream for stream in catalog.streams}

    for stream_name, _, _, cursor_field in _SYNC_TOKEN_STREAMS:
        stream = streams_by_name[stream_name]
        assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental], stream_name
        if cursor_field:
            assert stream.source_defined_cursor is True, stream_name
            assert stream.default_cursor_field == [cursor_field], stream_name
    for stream_name in _FULL_REFRESH_STREAMS:
        assert streams_by_name[stream_name].supported_sync_modes == [SyncMode.full_refresh], stream_name
    assert streams_by_name["applications"].default_cursor_field == ["updatedAt"]
