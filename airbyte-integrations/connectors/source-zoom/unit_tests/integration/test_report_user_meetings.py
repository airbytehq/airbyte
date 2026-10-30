# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import date
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
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


_STREAM = "report_user_meetings"
_WINDOWS = [
    ("2026-04-21", "2026-05-18"),
    ("2026-05-19", "2026-06-15"),
    ("2026-06-16", "2026-07-13"),
    ("2026-07-14", "2026-08-10"),
    ("2026-08-11", "2026-09-07"),
    ("2026-09-08", "2026-10-05"),
    ("2026-10-06", "2026-10-20"),
]
_FULL_28_DAY_WINDOWS = [("2026-08-26", "2026-09-22"), ("2026-09-23", "2026-10-20")]
_USER_ID = "u1"


def _report_request(start: str, end: str, next_page_token: str = "", user_id: str = _USER_ID):
    params = {"type": "past", "page_size": "300", "from": start, "to": end}
    if next_page_token:
        params["next_page_token"] = next_page_token
    return request(f"/report/users/{user_id}/meetings", params)


def _meeting(end_time: str, uuid: str = "meeting-uuid"):
    return {"uuid": uuid, "end_time": end_time, "topic": "Team sync"}


def _global_state(end_time: str) -> dict[str, object]:
    return {
        "use_global_cursor": True,
        "state": {"end_time": end_time},
        "lookback_window": 0,
        "parent_state": {},
    }


def _mock_parents(http_mocker: HttpMocker) -> None:
    mock_token(http_mocker)
    mock_users(http_mocker)


def _mock_windows(http_mocker: HttpMocker, failed_window=None, windows=_WINDOWS) -> list:
    requests = []
    for start, end in windows:
        current = _report_request(start, end)
        requests.append(current)
        if (start, end) == failed_window:
            http_mocker.get(current, zoom_error(300, "The request is outside the last six months.", status_code=400))
        elif end == "2026-10-20":
            http_mocker.get(current, json_response({"meetings": [_meeting("2026-10-19T12:00:00Z")]}))
        else:
            http_mocker.get(current, json_response({"meetings": []}))
    return requests


@freezegun.freeze_time("2026-10-20T12:00:00Z")
class TestReportUserMeetings(TestCase):
    @HttpMocker()
    def test_initial_sync_uses_exact_28_day_windows_and_emits_state(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        requests = _mock_windows(http_mocker, windows=_FULL_28_DAY_WINDOWS)

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-08-26T00:00:00Z"},
            sync_mode=SyncMode.incremental,
        )

        assert_completed_without_errors(output, _STREAM)
        assert records_data(output) == [{**_meeting("2026-10-19T12:00:00Z"), "user_id": _USER_ID}]
        assert all((date.fromisoformat(end) - date.fromisoformat(start)).days == 27 for start, end in _FULL_28_DAY_WINDOWS)
        emitted_state = output.most_recent_state.stream_state.__dict__
        assert emitted_state["use_global_cursor"] is True
        assert emitted_state["state"] == {"end_time": "2026-10-19"}
        for http_request in requests:
            http_mocker.assert_number_of_calls(http_request, 1)

    @HttpMocker()
    def test_start_date_sets_the_initial_window(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        requests = [
            _report_request("2026-09-01", "2026-09-28"),
            _report_request("2026-09-29", "2026-10-20"),
        ]
        for current in requests:
            http_mocker.get(current, json_response({"meetings": []}))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-09-01T00:00:00Z"},
            sync_mode=SyncMode.incremental,
        )

        assert_completed_without_errors(output, _STREAM)
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_start_date_older_than_zoom_retention_is_clamped(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        requests = _mock_windows(http_mocker)

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2025-01-01T00:00:00Z"},
            sync_mode=SyncMode.incremental,
        )

        assert_completed_without_errors(output, _STREAM)
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_paginates_within_a_window(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        first = _report_request("2026-10-18", "2026-10-20")
        second = _report_request("2026-10-18", "2026-10-20", "next-page")
        http_mocker.get(first, json_response({"meetings": [_meeting("2026-10-19T12:00:00Z", "first")], "next_page_token": "next-page"}))
        http_mocker.get(second, json_response({"meetings": [_meeting("2026-10-20T10:00:00Z", "second")]}))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-10-18T00:00:00Z"},
            sync_mode=SyncMode.incremental,
        )

        assert_completed_without_errors(output, _STREAM)
        assert {record["uuid"] for record in records_data(output)} == {"first", "second"}
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)

    @HttpMocker()
    def test_incremental_state_uses_lookback_date(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        current = _report_request("2026-10-09", "2026-10-20")
        http_mocker.get(current, json_response({"meetings": []}))

        output = read_stream(
            _STREAM,
            sync_mode=SyncMode.incremental,
            state=StateBuilder().with_stream_state(_STREAM, _global_state("2026-10-10")).build(),
        )

        assert_completed_without_errors(output, _STREAM)
        http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_global_cursor_uses_one_window_for_users_without_prior_meetings(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        mock_users(http_mocker, users=[{"id": "u1"}, {"id": "u2"}])
        requests = [
            _report_request("2026-10-09", "2026-10-20", user_id="u1"),
            _report_request("2026-10-09", "2026-10-20", user_id="u2"),
        ]
        http_mocker.get(requests[0], json_response({"meetings": [_meeting("2026-10-10T12:00:00Z")]}))
        http_mocker.get(requests[1], json_response({"meetings": []}))

        output = read_stream(
            _STREAM,
            sync_mode=SyncMode.incremental,
            state=StateBuilder().with_stream_state(_STREAM, _global_state("2026-10-10")).build(),
        )

        assert_completed_without_errors(output, _STREAM)
        assert records_data(output) == [{**_meeting("2026-10-10T12:00:00Z"), "user_id": "u1"}]
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_unknown_user_is_ignored(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        current = _report_request("2026-10-19", "2026-10-20")
        http_mocker.get(current, zoom_error(1001, "User does not exist.", status_code=404))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-10-19T00:00:00Z"},
            sync_mode=SyncMode.incremental,
        )

        assert_completed_without_errors(output, _STREAM)
        assert output.records == []
        http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_six_months_code_300_is_ignored_for_only_the_expired_window(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        requests = _mock_windows(http_mocker, failed_window=_WINDOWS[0])

        output = read_stream(_STREAM, sync_mode=SyncMode.incremental)

        assert_completed_without_errors(output, _STREAM)
        assert records_data(output) == [{**_meeting("2026-10-19T12:00:00Z"), "user_id": _USER_ID}]
        assert output.is_in_logs("Zoom keeps reports for six months only")
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_report_plan_error_is_configuration_error(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        current = _report_request("2026-10-19", "2026-10-20")
        http_mocker.get(current, zoom_error(200, "Reports require a paid account.", status_code=400))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-10-19T00:00:00Z"},
            sync_mode=SyncMode.incremental,
            expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION,
        )

        assert_failed_with_config_error(output, _STREAM)
        assert output.is_in_logs("Pro or higher plan")
        assert output.is_in_logs("report:read:admin")
        assert output.is_in_logs("report:read:user:admin")
        http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_missing_scope_is_configuration_error(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        current = _report_request("2026-10-19", "2026-10-20")
        http_mocker.get(current, zoom_error(4711, "Missing report scope.", status_code=400))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-10-19T00:00:00Z"},
            sync_mode=SyncMode.incremental,
            expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION,
        )

        assert_failed_with_config_error(output, _STREAM)
        assert output.is_in_logs("report:read:admin")
        assert output.is_in_logs("report:read:user:admin")
        http_mocker.assert_number_of_calls(current, 1)
