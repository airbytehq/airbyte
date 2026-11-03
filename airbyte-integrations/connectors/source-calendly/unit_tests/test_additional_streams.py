# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

import pytest
import yaml
from _helpers import ORGANIZATION_URI, collection, mock_user, read_stream, request
from conftest import _YAML_FILE_PATH
from freezegun import freeze_time
from jsonschema import Draft7Validator

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


NOW = "2024-02-01T00:00:00.000000Z"
START = "2024-01-01T00:00:00.000000Z"
SAVED = "2024-01-10T00:00:00.000000Z"
FORM_URIS = [f"https://api.calendly.com/routing_forms/{name}" for name in ["one", "two"]]
INCREMENTAL = {
    "outgoing_communications": ("created_at", "min_created_at", "max_created_at"),
    "activity_log_entries": ("occurred_at", "min_occurred_at", "max_occurred_at"),
    "meeting_recaps": ("start_time", "start_time", "end_time"),
}
PLAN_GATED = list(INCREMENTAL)
PLAN_MESSAGES = [
    "Please upgrade your Calendly account to Enterprise.",
    "Please upgrade to a paid Calendly account",
    "Meeting recap access is not available. Required features are not enabled for your account",
]


def test_new_stream_keys_match_documented_api_fields() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    for stream in ["routing_forms", "routing_form_submissions", "contacts", *INCREMENTAL]:
        definition = manifest["definitions"]["streams"][stream]
        schema = manifest["schemas"][stream]
        if stream == "outgoing_communications":
            assert definition["primary_key"] == []
            assert "uri" not in schema["properties"]
            assert {"created_at", "event_uri", "type", "to"} <= schema["properties"].keys()
        else:
            assert definition["primary_key"] == ["uri"]
            assert schema["properties"]["uri"]["type"] == "string"


def stream_request(stream: str, page_token: str | None = None, start: str = START) -> HttpRequest:
    params = {"count": "100"}
    if stream in {"routing_forms", "outgoing_communications", "activity_log_entries"}:
        params["organization"] = ORGANIZATION_URI
    if stream == "activity_log_entries":
        params["sort"] = "occurred_at:asc"
    if stream in INCREMENTAL:
        _, lower, upper = INCREMENTAL[stream]
        params.update({lower: start, upper: NOW})
    if page_token:
        params["page_token"] = page_token
    return request(stream, params)


def assert_complete(output: EntrypointOutput, stream: str) -> None:
    assert not output.errors
    assert any(
        message.trace.stream_status.stream_descriptor.name == stream and message.trace.stream_status.status.value == "COMPLETE"
        for message in output.get_message_by_types([Type.TRACE])
        if message.trace.stream_status
    )
    schema = yaml.safe_load(_YAML_FILE_PATH.read_text())["schemas"][stream]
    for message in output.records:
        Draft7Validator(schema).validate(message.record.data)


def incremental_record(stream: str, index: int, timestamp: str) -> dict[str, Any]:
    cursor, _, _ = INCREMENTAL[stream]
    if stream == "outgoing_communications":
        return {
            "type": "email" if index == 1 else "sms",
            "to": "invitee@example.com" if index == 1 else "+15555550100",
            "from": "host@example.com" if index == 1 else "+15555550101",
            "body": "Meeting reminder",
            "event_uri": f"https://api.calendly.com/scheduled_events/{index}",
            cursor: timestamp,
        }
    record: dict[str, Any] = {"uri": f"https://api.calendly.com/{stream}/{index}", cursor: timestamp}
    if stream == "activity_log_entries":
        record.update(actor={"uri": "https://api.calendly.com/users/test-user", "type": "User"}, details={"changed_field": "name"})
    else:
        record.update(
            status="Available",
            location={"type": "zoom_conference", "join_url": "https://example.com/meeting"},
            attendees=[{"host": True, "user_email": "host@example.com", "user_name": "Test Host"}],
            transcript="Meeting transcript",
        )
    return record


def test_routing_forms_pages_with_organization() -> None:
    records = [
        {"uri": uri, "name": f"Form {index}", "questions": [{"uuid": "question-id", "name": "Company", "type": "text", "required": False}]}
        for index, uri in enumerate(FORM_URIS)
    ]
    with HttpMocker() as http:
        user = mock_user(http)
        first, second = stream_request("routing_forms"), stream_request("routing_forms", "next-token")
        http.get(first, collection(records[:1], "next-token"))
        http.get(second, collection(records[1:]))
        output = read_stream("routing_forms", sync_mode=SyncMode.full_refresh)
        assert_complete(output, "routing_forms")
        assert [r.record.data for r in output.records] == records
        for target in [user, first, second]:
            http.assert_number_of_calls(target, 1)


def test_routing_form_submissions_pages_for_each_parent_form() -> None:
    with HttpMocker() as http:
        mock_user(http)
        parent_first = stream_request("routing_forms")
        parent_second = stream_request("routing_forms", "parents-next")
        http.get(parent_first, collection([{"uri": FORM_URIS[0]}], "parents-next"))
        http.get(parent_second, collection([{"uri": FORM_URIS[1]}]))
        targets = [parent_first, parent_second]
        expected = []
        for form in FORM_URIS:
            params = {"count": "100", "sort": "created_at:asc", "form": form}
            first = request("routing_form_submissions", params)
            second = request("routing_form_submissions", {**params, "page_token": "submissions-next"})
            records = [{"uri": f"{form}/submissions/{index}", "routing_form": form} for index in [1, 2]]
            expected.extend(records)
            targets.extend([first, second])
            http.get(first, collection(records[:1], "submissions-next"))
            http.get(second, collection(records[1:]))
        output = read_stream("routing_form_submissions", sync_mode=SyncMode.full_refresh)
        assert_complete(output, "routing_form_submissions")
        assert sorted((r.record.data for r in output.records), key=lambda r: r["uri"]) == expected
        for target in targets:
            http.assert_number_of_calls(target, 1)


def test_contacts_pages_without_organization_filter() -> None:
    records = [
        {
            "uri": f"https://api.calendly.com/contacts/{index}",
            "name": f"Contact {index}",
            "emails": [{"email": f"contact{index}@example.com", "is_primary": True}],
            "phone_numbers": [{"phone_number": "+15555550100"}],
            "custom_fields": [{"uri": "https://api.calendly.com/contact_custom_fields/test", "label": "Company", "value": "Example"}],
        }
        for index in [1, 2]
    ]
    with HttpMocker() as http:
        first, second = stream_request("contacts"), stream_request("contacts", "next-token")
        http.get(first, collection(records[:1], "next-token"))
        http.get(second, collection(records[1:]))
        output = read_stream("contacts", sync_mode=SyncMode.full_refresh)
        assert_complete(output, "contacts")
        assert [r.record.data for r in output.records] == records
        for target in [first, second]:
            http.assert_number_of_calls(target, 1)


@freeze_time(NOW)
@pytest.mark.parametrize("stream", INCREMENTAL)
@pytest.mark.parametrize("resume", [False, True])
def test_incremental_stream_pages_with_bounded_window_and_state(stream: str, resume: bool) -> None:
    cursor, _, _ = INCREMENTAL[stream]
    saved_state: dict[str, Any] = {cursor: SAVED}
    if stream != "meeting_recaps":
        saved_state = {"state": saved_state, "use_global_cursor": True, "parent_state": {}, "lookback_window": 0}
    state = StateBuilder().with_stream_state(stream, saved_state).build() if resume else None
    start = SAVED if resume else START
    records = [incremental_record(stream, index, f"2024-01-{day}T00:00:00.000000Z") for index, day in [(1, 15), (2, 20)]]
    future = incremental_record(stream, 3, "2024-03-01T00:00:00.000000Z")
    with HttpMocker() as http:
        if stream != "meeting_recaps":
            user = mock_user(http)
        first, second = stream_request(stream, start=start), stream_request(stream, "next-token", start=start)
        http.get(first, collection(records[:1], "next-token"))
        http.get(second, collection([records[1], future]))
        output = read_stream(stream, state=state)
        assert_complete(output, stream)
        assert [r.record.data for r in output.records] == records
        expected_state: dict[str, Any] = {cursor: records[-1][cursor]}
        if stream != "meeting_recaps":
            expected_state = {"state": expected_state, "use_global_cursor": True, "parent_state": {}, "lookback_window": 0}
        assert output.most_recent_state.stream_state.__dict__ == expected_state
        for target in [first, second]:
            http.assert_number_of_calls(target, 1)
        if stream != "meeting_recaps":
            http.assert_number_of_calls(user, 1)


@freeze_time(NOW)
@pytest.mark.parametrize("stream", PLAN_GATED)
@pytest.mark.parametrize("message", PLAN_MESSAGES)
def test_plan_gating_completes_empty_with_warning(stream: str, message: str) -> None:
    with HttpMocker() as http:
        mock_user(http)
        target = stream_request(stream)
        http.get(target, HttpResponse(body=json.dumps({"title": "Permission Denied", "message": message}), status_code=403))
        output = read_stream(stream)
        assert_complete(output, stream)
        assert not output.records
        assert output.is_in_logs("Enterprise|Notetaker|paid")
        http.assert_number_of_calls(target, 1)


@freeze_time(NOW)
@pytest.mark.parametrize("stream", PLAN_GATED)
@pytest.mark.parametrize(
    "body",
    [
        {"message": "Insufficient scope", "required_scopes": ["meeting_recaps:read"]},
        {"message": "You do not have permission to access this resource."},
        {"message": "You do not have permission to access this resource"},
        {"message": "Unrecognized forbidden response"},
        {"message": PLAN_MESSAGES[0], "required_scopes": ["meeting_recaps:read"]},
        {"message": "Please upgrade your Calendly account to Enterprise. Unrecognized suffix"},
    ],
)
def test_other_forbidden_responses_still_fail(stream: str, body: dict[str, Any]) -> None:
    with HttpMocker() as http:
        mock_user(http)
        target = stream_request(stream)
        http.get(target, HttpResponse(body=json.dumps(body), status_code=403))
        output = read_stream(stream)
        assert not output.records
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert body["message"] in output.errors[0].trace.error.message
        if "required_scopes" in body:
            assert "meeting_recaps:read" in output.errors[0].trace.error.message
        http.assert_number_of_calls(target, 1)
