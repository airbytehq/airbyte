# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .zoom_mocks import (
    CONFIG,
    assert_completed_without_errors,
    json_response,
    mock_token,
    mock_users,
    read_stream,
    records_data,
    request,
)


_USER_ID = "u1"
_MEETINGS_REQUEST = request(f"/users/{_USER_ID}/meetings", {"page_size": "30"})
_MEETINGS = [
    {"id": 111, "created_at": "2026-09-01T10:00:00Z"},
    {"id": 222, "created_at": "2026-10-01T10:00:00Z"},
    {"id": 333, "created_at": "2026-10-10T10:00:00Z"},
]
_START_DATE_MEETINGS = [
    {"id": 444, "created_at": "2026-09-01T10:00:00Z"},
    {"id": 555, "created_at": "2026-10-10T10:00:00Z"},
]


def _mock_meetings(http_mocker: HttpMocker, meetings=_MEETINGS):
    mock_token(http_mocker)
    mock_users(http_mocker)
    http_mocker.get(_MEETINGS_REQUEST, json_response({"meetings": meetings, "next_page_token": ""}))
    detail_requests = {}
    for meeting in meetings:
        detail_request = request(f"/meetings/{meeting['id']}")
        http_mocker.get(
            detail_request,
            json_response({**meeting, "host_id": _USER_ID, "topic": f"Meeting {meeting['id']}"}),
        )
        detail_requests[meeting["id"]] = detail_request
    return detail_requests


def _state_from(output, stream_name: str):
    return StateBuilder().with_stream_state(stream_name, output.most_recent_state.stream_state.__dict__).build()


@freezegun.freeze_time("2026-10-20T12:00:00Z")
class TestIncrementalMeetingStreams(TestCase):
    def test_meetings_uses_parent_creation_time_state_and_lookback(self):
        with HttpMocker() as http_mocker:
            detail_requests = _mock_meetings(http_mocker)
            first = read_stream("meetings", sync_mode=SyncMode.incremental)
            http_mocker.assert_number_of_calls(_MEETINGS_REQUEST, 1)
            for meeting in _MEETINGS:
                http_mocker.assert_number_of_calls(detail_requests[meeting["id"]], 1)
        assert_completed_without_errors(first, "meetings")

        with HttpMocker() as http_mocker:
            detail_requests = _mock_meetings(http_mocker)
            second = read_stream(
                "meetings",
                sync_mode=SyncMode.incremental,
                state=_state_from(first, "meetings"),
            )
            http_mocker.assert_number_of_calls(_MEETINGS_REQUEST, 1)
            http_mocker.assert_number_of_calls(detail_requests[_MEETINGS[0]["id"]], 0)
            for meeting in _MEETINGS[1:]:
                http_mocker.assert_number_of_calls(detail_requests[meeting["id"]], 1)
        assert_completed_without_errors(second, "meetings")
        assert len(records_data(first)) == 3
        assert {record["created_at"] for record in records_data(second)} == {
            "2026-10-01T10:00:00Z",
            "2026-10-10T10:00:00Z",
        }

    def test_meetings_start_date_filters_first_sync(self):
        with HttpMocker() as http_mocker:
            detail_requests = _mock_meetings(http_mocker, _START_DATE_MEETINGS)
            output = read_stream(
                "meetings",
                config={**CONFIG, "start_date": "2026-10-01T00:00:00Z"},
                sync_mode=SyncMode.incremental,
            )
            http_mocker.assert_number_of_calls(_MEETINGS_REQUEST, 1)
            http_mocker.assert_number_of_calls(detail_requests[_START_DATE_MEETINGS[0]["id"]], 0)
            http_mocker.assert_number_of_calls(detail_requests[_START_DATE_MEETINGS[1]["id"]], 1)

        assert_completed_without_errors(output, "meetings")
        assert [record["created_at"] for record in records_data(output)] == ["2026-10-10T10:00:00Z"]

    def test_legacy_state_is_accepted_for_incremental_meeting_streams(self):
        with HttpMocker() as http_mocker:
            _mock_meetings(http_mocker)
            legacy_state = (
                StateBuilder()
                .with_stream_state(
                    "meetings",
                    {"__ab_no_cursor_state_message": True},
                )
                .build()
            )
            output = read_stream(
                "meetings",
                sync_mode=SyncMode.incremental,
                state=legacy_state,
            )
            http_mocker.assert_number_of_calls(_MEETINGS_REQUEST, 1)
        assert_completed_without_errors(output, "meetings")
