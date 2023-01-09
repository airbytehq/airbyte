#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy

import pendulum
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord, _RowValues
from source_bing_ads.reports import ReportsMixin
from source_bing_ads.source import SourceBingAds


class TestClient:
    pass


class TestReport(ReportsMixin, SourceBingAds):
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
