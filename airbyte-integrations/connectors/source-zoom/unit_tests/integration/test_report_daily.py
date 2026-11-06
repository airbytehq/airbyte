# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.models.outcome import ExpectedOutcome

from .zoom_mocks import (
    CONFIG,
    assert_completed_without_errors,
    assert_failed_with_config_error,
    json_response,
    mock_token,
    read_stream,
    records_data,
    request,
    zoom_error,
)


_STREAM = "report_daily"


def _daily_request(month: int):
    return request("/report/daily", {"year": "2026", "month": str(month)})


def _daily_record(date: str):
    return {"date": date, "meeting_minutes": 20, "meetings": 1, "new_users": 0, "participants": 2}


def _mock_months(http_mocker: HttpMocker, months):
    requests = []
    for month in months:
        current = _daily_request(month)
        requests.append(current)
        day = "20" if month == 10 else "15"
        http_mocker.get(current, json_response({"dates": [_daily_record(f"2026-{month:02d}-{day}")]}))
    return requests


@freezegun.freeze_time("2026-10-20T12:00:00Z")
class TestReportDaily(TestCase):
    @HttpMocker()
    def test_full_refresh_requests_each_recent_month(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        requests = _mock_months(http_mocker, range(5, 11))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(record["date"] for record in records_data(output)) == [
            "2026-05-15",
            "2026-06-15",
            "2026-07-15",
            "2026-08-15",
            "2026-09-15",
            "2026-10-20",
        ]
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_start_date_mid_month_includes_its_calendar_month(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        requests = _mock_months(http_mocker, (9, 10))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-09-15T00:00:00Z"},
        )

        assert_completed_without_errors(output, _STREAM)
        assert [record["date"] for record in records_data(output)] == ["2026-09-15", "2026-10-20"]
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_six_months_code_300_is_ignored_for_only_the_expired_month(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        requests = []
        for month in range(5, 11):
            current = _daily_request(month)
            requests.append(current)
            if month == 5:
                http_mocker.get(
                    current,
                    zoom_error(
                        300, "Daily report can only be provided for a month that falls within the recent 6 months.", status_code=400
                    ),
                )
            else:
                day = "20" if month == 10 else "15"
                http_mocker.get(current, json_response({"dates": [_daily_record(f"2026-{month:02d}-{day}")]}))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-05-01T00:00:00Z"},
        )

        assert_completed_without_errors(output, _STREAM)
        assert [record["date"] for record in records_data(output)] == [
            "2026-06-15",
            "2026-07-15",
            "2026-08-15",
            "2026-09-15",
            "2026-10-20",
        ]
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_missing_scope_is_configuration_error(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        current = _daily_request(10)
        http_mocker.get(current, zoom_error(4711, "Missing report scope.", status_code=400))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-10-19T00:00:00Z"},
            expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION,
        )

        assert_failed_with_config_error(output, _STREAM)
        assert output.is_in_logs("report:read:admin")
        assert output.is_in_logs("report:read:daily_usage:admin")
        http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_report_plan_error_is_configuration_error(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        current = _daily_request(10)
        http_mocker.get(current, zoom_error(200, "Reports require a paid account.", status_code=400))

        output = read_stream(
            _STREAM,
            config={**CONFIG, "start_date": "2026-10-19T00:00:00Z"},
            expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION,
        )

        assert_failed_with_config_error(output, _STREAM)
        assert output.is_in_logs("Pro or higher plan")
        assert output.is_in_logs("report:read:admin")
        assert output.is_in_logs("report:read:daily_usage:admin")
        http_mocker.assert_number_of_calls(current, 1)
