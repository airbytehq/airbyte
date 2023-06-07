#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy

import pendulum
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord, _RowValues
from source_bing_ads.reports import PerformanceReportsMixin, ReportsMixin
from source_bing_ads.source import SourceBingAds


class TestClient:
    pass


class TestReport(ReportsMixin, SourceBingAds):
    date_format, report_columns, report_name, cursor_field = "YYYY-MM-DD", None, None, "Time"
    report_aggregation = "Monthly"
    report_schema_name = "campaign_performance_report"

    def __init__(self) -> None:
        self.client = TestClient()


class TestPerformanceReport(PerformanceReportsMixin, SourceBingAds):
    date_format, report_columns, report_name, cursor_field = "YYYY-MM-DD", None, None, "Time"
    report_aggregation = "Monthly"
    report_schema_name = "campaign_performance_report"

    def __init__(self) -> None:
        self.client = TestClient()


def test_get_column_value():
    row_values = _RowValues(
        {"AccountId": 1, "AverageCpc": 3, "AdGroupId": 2, "AccountName": 5, "Spend": 4},
        {3: "11.5", 1: "33", 2: "--", 5: "123456789", 4: "120.3%"},
    )
    record = _RowReportRecord(row_values)

    test_report = TestReport()
    assert test_report.get_column_value(record, "AccountId") == 33
    assert test_report.get_column_value(record, "AverageCpc") == 11.5
    assert test_report.get_column_value(record, "AdGroupId") == 0
    assert test_report.get_column_value(record, "AccountName") == "123456789"
    assert test_report.get_column_value(record, "Spend") == 1.203


def test_get_updated_state_init_state():
    test_report = TestReport()
    stream_state = {}
    latest_record = {"AccountId": 123, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(stream_state, latest_record)
    assert new_state["123"]["Time"] == (pendulum.parse("2020-01-02")).timestamp()


def test_get_updated_state_new_state():
    test_report = TestReport()
    stream_state = {"123": {"Time": pendulum.parse("2020-01-01").timestamp()}}
    latest_record = {"AccountId": 123, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(stream_state, latest_record)
    assert new_state["123"]["Time"] == pendulum.parse("2020-01-02").timestamp()


def test_get_updated_state_state_unchanged():
    test_report = TestReport()
    stream_state = {"123": {"Time": pendulum.parse("2020-01-03").timestamp()}}
    latest_record = {"AccountId": 123, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(copy.deepcopy(stream_state), latest_record)
    assert stream_state == new_state


def test_get_updated_state_state_new_account():
    test_report = TestReport()
    stream_state = {"123": {"Time": pendulum.parse("2020-01-03").timestamp()}}
    latest_record = {"AccountId": 234, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(stream_state, latest_record)
    assert "234" in new_state and "123" in new_state
    assert new_state["234"]["Time"] == pendulum.parse("2020-01-02").timestamp()


def test_get_report_record_timestamp_daily():
    test_report = TestReport()
    test_report.report_aggregation = "Daily"
    assert pendulum.parse("2020-01-01").timestamp() == test_report.get_report_record_timestamp("2020-01-01")


def test_get_report_record_timestamp_without_aggregation():
    test_report = TestReport()
    test_report.report_aggregation = None
    assert pendulum.parse("2020-07-20").timestamp() == test_report.get_report_record_timestamp("7/20/2020")


def test_get_report_record_timestamp_hourly():
    test_report = TestReport()
    test_report.report_aggregation = "Hourly"
    assert pendulum.parse("2020-01-01T15:00:00").timestamp() == test_report.get_report_record_timestamp("2020-01-01|15")


def test_report_get_start_date_wo_stream_state():
    expected_start_date = "2020-01-01"
    test_report = TestReport()
    test_report.client.reports_start_date = "2020-01-01"
    stream_state = {}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_with_stream_state():
    expected_start_date = pendulum.parse("2023-04-17T21:29:57")
    test_report = TestReport()
    test_report.cursor_field = "cursor_field"
    test_report.client.reports_start_date = "2020-01-01"
    stream_state = {"123": {"cursor_field": 1681766997}}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_performance_report_with_stream_state():
    expected_start_date = pendulum.parse("2023-04-07T21:29:57")
    test_report = TestPerformanceReport()
    test_report.cursor_field = "cursor_field"
    test_report.config = {"lookback_window": 10}
    stream_state = {"123": {"cursor_field": 1681766997}}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_performance_report_wo_stream_state():
    days_to_subtract = 10
    reports_start_date = pendulum.parse("2021-04-07T00:00:00")
    test_report = TestPerformanceReport()
    test_report.cursor_field = "cursor_field"
    test_report.client.reports_start_date = reports_start_date
    test_report.config = {"lookback_window": days_to_subtract}
    stream_state = {}
    account_id = "123"
    assert reports_start_date.subtract(days=days_to_subtract) == test_report.get_start_date(stream_state, account_id)
