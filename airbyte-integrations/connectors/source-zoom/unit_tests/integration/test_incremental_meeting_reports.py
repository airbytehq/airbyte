# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.models.outcome import ExpectedOutcome
from airbyte_cdk.test.state_builder import StateBuilder

from .zoom_mocks import (
    CONFIG,
    assert_completed_without_errors,
    assert_failed_with_config_error,
    json_response,
    mock_token,
    mock_users,
    read_stream,
    records_data,
    request,
    zoom_error,
)


_USER_ID = "u1"
_PAGE_SIZE = "30"
_START_DATE = "2026-10-09T00:00:00Z"
_BEFORE_END_REQUEST = request(
    f"/report/users/{_USER_ID}/meetings",
    ANY_QUERY_PARAMS,
)
_AFTER_END_REQUEST = request(
    f"/report/users/{_USER_ID}/meetings",
    ANY_QUERY_PARAMS,
)
_PRIOR_SESSION = {
    "uuid": "prior-session",
    "id": 123,
    "end_time": "2026-10-10T11:00:00Z",
}
_LATE_SESSION = {
    "uuid": "late-session",
    "id": 123,
    "end_time": "2026-10-11T11:00:00Z",
}


def _report_request(stream_name: str, uuid: str):
    path = f"/report/meetings/{uuid}"
    if stream_name == "report_meeting_participants":
        path += "/participants"
        return request(path, {"page_size": _PAGE_SIZE})
    return request(path)


def _mock_parent_chain(http_mocker: HttpMocker, parent_request, meetings):
    mock_token(http_mocker)
    users_request = mock_users(http_mocker)
    http_mocker.get(parent_request, json_response({"meetings": meetings}))
    return users_request


def _report_response(meeting):
    return {
        **meeting,
        "start_time": "2026-10-11T10:00:00Z",
        "topic": "Recurring meeting",
    }


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("report_meetings", id="meeting-report"),
        pytest.param("report_meeting_participants", id="meeting-participants"),
    ],
)
def test_late_meeting_reports_resume_after_session_end(stream_name):
    late_report_request = _report_request(stream_name, _LATE_SESSION["uuid"])
    prior_report_request = _report_request(stream_name, _PRIOR_SESSION["uuid"])

    with freezegun.freeze_time("2026-10-10T12:00:00Z"):
        with HttpMocker() as http_mocker:
            users_request = _mock_parent_chain(http_mocker, _BEFORE_END_REQUEST, [_PRIOR_SESSION])
            http_mocker.get(prior_report_request, zoom_error(300, "No report is available.", status_code=404))
            http_mocker.get(late_report_request, json_response(_report_response(_LATE_SESSION)))
            first = read_stream(
                stream_name,
                config={**CONFIG, "start_date": _START_DATE},
                sync_mode=SyncMode.incremental,
            )
            http_mocker.assert_number_of_calls(users_request, 1)
            http_mocker.assert_number_of_calls(_BEFORE_END_REQUEST, 1)
            http_mocker.assert_number_of_calls(prior_report_request, 1)
            http_mocker.assert_number_of_calls(late_report_request, 0)

    assert_completed_without_errors(first, stream_name)
    assert records_data(first) == []

    state = StateBuilder().with_stream_state(stream_name, first.most_recent_state.stream_state.__dict__).build()
    with freezegun.freeze_time("2026-10-12T12:00:00Z"):
        with HttpMocker() as http_mocker:
            users_request = _mock_parent_chain(http_mocker, _AFTER_END_REQUEST, [_LATE_SESSION])
            if stream_name == "report_meeting_participants":
                http_mocker.get(
                    late_report_request,
                    json_response(
                        {
                            "participants": [
                                {
                                    "id": "participant-1",
                                    "user_id": "attendee-1",
                                    "join_time": "2026-10-11T10:00:00Z",
                                    "leave_time": "2026-10-11T11:00:00Z",
                                }
                            ],
                            "next_page_token": "",
                        }
                    ),
                )
            else:
                http_mocker.get(late_report_request, json_response(_report_response(_LATE_SESSION)))
            second = read_stream(
                stream_name,
                config={**CONFIG, "start_date": _START_DATE},
                sync_mode=SyncMode.incremental,
                state=state,
            )
            http_mocker.assert_number_of_calls(users_request, 1)
            http_mocker.assert_number_of_calls(_AFTER_END_REQUEST, 1)
            http_mocker.assert_number_of_calls(late_report_request, 1)

    assert_completed_without_errors(second, stream_name)
    if stream_name == "report_meeting_participants":
        emitted_state = second.most_recent_state.stream_state.__dict__
        assert emitted_state["state"] == {"meeting_end_time": "2026-10-11"}
        assert records_data(second) == [
            {
                "id": "participant-1",
                "user_id": "attendee-1",
                "join_time": "2026-10-11T10:00:00Z",
                "leave_time": "2026-10-11T11:00:00Z",
                "meeting_id": _LATE_SESSION["id"],
                "meeting_uuid": _LATE_SESSION["uuid"],
                "meeting_end_time": _LATE_SESSION["end_time"],
            }
        ]
    else:
        assert records_data(second) == [_report_response(_LATE_SESSION)]


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("report_meetings", id="meeting-report"),
        pytest.param("report_meeting_participants", id="meeting-participants"),
    ],
)
def test_meeting_report_streams_accept_legacy_state(stream_name):
    late_report_request = _report_request(stream_name, _LATE_SESSION["uuid"])
    parent_request = request(f"/report/users/{_USER_ID}/meetings", ANY_QUERY_PARAMS)

    with freezegun.freeze_time("2026-10-12T12:00:00Z"):
        with HttpMocker() as http_mocker:
            users_request = _mock_parent_chain(http_mocker, parent_request, [_LATE_SESSION])
            if stream_name == "report_meeting_participants":
                http_mocker.get(
                    late_report_request,
                    json_response(
                        {
                            "participants": [
                                {
                                    "id": "participant-1",
                                    "user_id": "attendee-1",
                                    "join_time": "2026-10-11T10:00:00Z",
                                    "leave_time": "2026-10-11T11:00:00Z",
                                }
                            ],
                            "next_page_token": "",
                        }
                    ),
                )
            else:
                http_mocker.get(late_report_request, json_response(_report_response(_LATE_SESSION)))

            legacy_state = StateBuilder().with_stream_state(stream_name, {"__ab_no_cursor_state_message": True}).build()
            output = read_stream(
                stream_name,
                config={**CONFIG, "start_date": _START_DATE},
                sync_mode=SyncMode.incremental,
                state=legacy_state,
            )
            http_mocker.assert_number_of_calls(users_request, 1)
            http_mocker.assert_number_of_calls(parent_request, 1)
            http_mocker.assert_number_of_calls(late_report_request, 1)

    assert_completed_without_errors(output, stream_name)
    if stream_name == "report_meeting_participants":
        assert records_data(output) == [
            {
                "id": "participant-1",
                "user_id": "attendee-1",
                "join_time": "2026-10-11T10:00:00Z",
                "leave_time": "2026-10-11T11:00:00Z",
                "meeting_id": _LATE_SESSION["id"],
                "meeting_uuid": _LATE_SESSION["uuid"],
                "meeting_end_time": _LATE_SESSION["end_time"],
            }
        ]
    else:
        assert records_data(output) == [_report_response(_LATE_SESSION)]


def test_report_meetings_missing_scope_fails_with_granular_scope_error():
    parent_request = request(f"/report/users/{_USER_ID}/meetings", ANY_QUERY_PARAMS)

    with freezegun.freeze_time("2026-10-12T12:00:00Z"):
        with HttpMocker() as http_mocker:
            mock_token(http_mocker)
            users_request = mock_users(http_mocker)
            http_mocker.get(parent_request, zoom_error(4711, "Missing report scope.", status_code=400))
            output = read_stream(
                "report_meetings",
                config={**CONFIG, "start_date": _START_DATE},
                expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION,
                sync_mode=SyncMode.incremental,
            )
            http_mocker.assert_number_of_calls(users_request, 1)
            http_mocker.assert_number_of_calls(parent_request, 1)

    assert_failed_with_config_error(output, "report_meetings")
    assert output.is_in_logs("report:read:user:admin")


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("report_meetings", id="meeting-report"),
        pytest.param("report_meeting_participants", id="meeting-participants"),
    ],
)
def test_recurring_meeting_sessions_have_distinct_keys_and_encoded_paths(stream_name):
    sessions = [
        {"uuid": "session-one", "id": 321, "end_time": "2026-10-10T11:00:00Z"},
        {"uuid": "session/2==", "id": 321, "end_time": "2026-10-10T12:00:00Z"},
    ]
    with freezegun.freeze_time("2026-10-10T12:30:00Z"):
        parent_request = request(
            f"/report/users/{_USER_ID}/meetings",
            {"type": "past", "page_size": "300", "from": "2026-10-10", "to": "2026-10-10"},
        )
        report_requests = [
            request(
                f"/report/meetings/{uuid}" + ("/participants" if stream_name == "report_meeting_participants" else ""),
                {"page_size": _PAGE_SIZE} if stream_name == "report_meeting_participants" else None,
            )
            for uuid in ("session-one", "session%252F2%253D%253D")
        ]
        with HttpMocker() as http_mocker:
            users_request = _mock_parent_chain(http_mocker, parent_request, sessions)
            for session, report_api_request in zip(sessions, report_requests):
                if stream_name == "report_meeting_participants":
                    http_mocker.get(
                        report_api_request,
                        json_response(
                            {
                                "participants": [
                                    {
                                        "id": "participant-1",
                                        "user_id": "attendee-1",
                                        "join_time": "2026-10-10T10:00:00Z",
                                        "leave_time": "2026-10-10T11:00:00Z",
                                    }
                                ],
                                "next_page_token": "",
                            }
                        ),
                    )
                else:
                    http_mocker.get(report_api_request, json_response(_report_response(session)))
            output = read_stream(
                stream_name,
                config={**CONFIG, "start_date": "2026-10-10T00:00:00Z"},
                sync_mode=SyncMode.incremental,
            )
            http_mocker.assert_number_of_calls(users_request, 1)
            http_mocker.assert_number_of_calls(parent_request, 1)
            for report_api_request in report_requests:
                http_mocker.assert_number_of_calls(report_api_request, 1)

    assert_completed_without_errors(output, stream_name)
    records = records_data(output)
    assert len(records) == 2
    if stream_name == "report_meeting_participants":
        assert {(record["meeting_uuid"], record["user_id"]) for record in records} == {
            ("session-one", "attendee-1"),
            ("session/2==", "attendee-1"),
        }
        assert {record["meeting_id"] for record in records} == {321}
    else:
        assert {record["uuid"] for record in records} == {"session-one", "session/2=="}
