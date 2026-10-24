# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .zoom_mocks import (
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
    {"id": 222, "created_at": "2026-10-10T10:00:00Z"},
]


def _mock_meetings(http_mocker: HttpMocker, stream_name: str) -> None:
    mock_token(http_mocker)
    mock_users(http_mocker)
    http_mocker.get(_MEETINGS_REQUEST, json_response({"meetings": _MEETINGS, "next_page_token": ""}))
    if stream_name == "meetings":
        for meeting in _MEETINGS:
            http_mocker.get(
                request(f"/meetings/{meeting['id']}"),
                json_response({**meeting, "host_id": _USER_ID, "topic": f"Meeting {meeting['id']}"}),
            )
    elif stream_name == "report_meetings":
        for meeting in _MEETINGS:
            http_mocker.get(
                request(f"/report/meetings/{meeting['id']}"),
                json_response(
                    {
                        **meeting,
                        "uuid": f"uuid-{meeting['id']}",
                        "start_time": "2026-10-10T10:00:00Z",
                        "end_time": "2026-10-10T11:00:00Z",
                        "host_id": _USER_ID,
                        "topic": f"Meeting {meeting['id']}",
                    }
                ),
            )
    else:
        for meeting in _MEETINGS:
            http_mocker.get(
                request(f"/report/meetings/{meeting['id']}/participants", {"page_size": "30"}),
                json_response(
                    {
                        "participants": [
                            {
                                "id": "",
                                "user_id": f"user-{meeting['id']}",
                                "name": f"Guest {meeting['id']}",
                                "join_time": "2026-10-10T10:00:00Z",
                                "leave_time": "2026-10-10T11:00:00Z",
                            }
                        ],
                        "next_page_token": "",
                    }
                ),
            )


def _state_from(output, stream_name: str):
    return StateBuilder().with_stream_state(stream_name, output.most_recent_state.stream_state.__dict__).build()


@freezegun.freeze_time("2026-10-20T12:00:00Z")
class TestIncrementalMeetingStreams(TestCase):
    def _assert_two_syncs(self, stream_name: str) -> None:
        with HttpMocker() as http_mocker:
            _mock_meetings(http_mocker, stream_name)
            first = read_stream(stream_name, sync_mode=SyncMode.incremental)
        assert_completed_without_errors(first, stream_name)

        with HttpMocker() as http_mocker:
            _mock_meetings(http_mocker, stream_name)
            second = read_stream(
                stream_name,
                sync_mode=SyncMode.incremental,
                state=_state_from(first, stream_name),
            )
        assert_completed_without_errors(second, stream_name)
        assert len(records_data(first)) == 2
        assert len(records_data(second)) == 1
        assert records_data(second)[0].get("created_at", records_data(second)[0].get("meeting_created_at")) == ("2026-10-10T10:00:00Z")

    def test_meetings_uses_parent_creation_time_state(self):
        self._assert_two_syncs("meetings")

    def test_report_meetings_uses_parent_creation_time_state(self):
        self._assert_two_syncs("report_meetings")

    def test_report_meeting_participants_uses_parent_creation_time_state(self):
        self._assert_two_syncs("report_meeting_participants")

    def test_legacy_state_is_accepted_for_incremental_meeting_streams(self):
        for stream_name in ("meetings", "report_meetings", "report_meeting_participants"):
            with HttpMocker() as http_mocker:
                _mock_meetings(http_mocker, stream_name)
                legacy_state = (
                    StateBuilder()
                    .with_stream_state(
                        stream_name,
                        {"__ab_no_cursor_state_message": True},
                    )
                    .build()
                )
                output = read_stream(
                    stream_name,
                    sync_mode=SyncMode.incremental,
                    state=legacy_state,
                )
            assert_completed_without_errors(output, stream_name)
