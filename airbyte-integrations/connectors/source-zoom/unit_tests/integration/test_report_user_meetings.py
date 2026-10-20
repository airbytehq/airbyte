# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

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
    ("2026-04-21", "2026-05-20"),
    ("2026-05-21", "2026-06-19"),
    ("2026-06-20", "2026-07-19"),
    ("2026-07-20", "2026-08-18"),
    ("2026-08-19", "2026-09-17"),
    ("2026-09-18", "2026-10-17"),
    ("2026-10-18", "2026-10-20"),
]
_USER_ID = "u1"


def _report_request(start: str, end: str, next_page_token: str = ""):
    params = {"type": "past", "page_size": "300", "from": start, "to": end}
    if next_page_token:
        params["next_page_token"] = next_page_token
    return request(f"/report/users/{_USER_ID}/meetings", params)


def _meeting(end_time: str, uuid: str = "meeting-uuid"):
    return {"uuid": uuid, "end_time": end_time, "topic": "Team sync"}


def _mock_parents(http_mocker: HttpMocker) -> None:
    mock_token(http_mocker)
    mock_users(http_mocker)


def _mock_windows(http_mocker: HttpMocker, failed_window=None) -> list:
    requests = []
    for start, end in _WINDOWS:
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
    def test_initial_sync_uses_exact_30_day_windows_and_emits_state(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        requests = _mock_windows(http_mocker)

        output = read_stream(_STREAM, sync_mode=SyncMode.incremental)

        assert_completed_without_errors(output, _STREAM)
        assert records_data(output) == [{**_meeting("2026-10-19T12:00:00Z"), "user_id": _USER_ID}]
        assert output.most_recent_state.stream_state.__dict__["states"] == [
            {
                "partition": {"parent_id": _USER_ID, "parent_slice": {}},
                "cursor": {"end_time": "2026-10-19"},
            }
        ]
        for http_request in requests:
            http_mocker.assert_number_of_calls(http_request, 1)

    @HttpMocker()
    def test_start_date_sets_the_initial_window(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        requests = [
            _report_request("2026-09-01", "2026-09-30"),
            _report_request("2026-10-01", "2026-10-20"),
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
            state=StateBuilder()
            .with_stream_state(
                _STREAM,
                {
                    "states": [
                        {
                            "partition": {"parent_id": _USER_ID, "parent_slice": {}},
                            "cursor": {"end_time": "2026-10-10"},
                        }
                    ]
                },
            )
            .build(),
        )

        assert_completed_without_errors(output, _STREAM)
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
        http_mocker.assert_number_of_calls(current, 1)
