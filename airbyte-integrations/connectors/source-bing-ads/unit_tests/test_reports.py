#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from unittest.mock import Mock

import pendulum
import pytest
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord, _RowValues
from source_bing_ads.report_streams import (
    AccountImpressionPerformanceReportDaily,
    AccountImpressionPerformanceReportHourly,
    AccountPerformanceReportDaily,
    AccountPerformanceReportHourly,
    AdGroupImpressionPerformanceReportDaily,
    AdGroupImpressionPerformanceReportHourly,
    AdGroupPerformanceReportDaily,
    AdGroupPerformanceReportHourly,
    AdPerformanceReportDaily,
    AdPerformanceReportHourly,
    AgeGenderAudienceReportDaily,
    AgeGenderAudienceReportHourly,
    BingAdsReportingServicePerformanceStream,
    BingAdsReportingServiceStream,
    BudgetSummaryReport,
    CampaignImpressionPerformanceReportDaily,
    CampaignImpressionPerformanceReportHourly,
    CampaignPerformanceReportDaily,
    CampaignPerformanceReportHourly,
    GeographicPerformanceReportDaily,
    GeographicPerformanceReportHourly,
    GeographicPerformanceReportMonthly,
    GeographicPerformanceReportWeekly,
    KeywordPerformanceReportDaily,
    KeywordPerformanceReportHourly,
    SearchQueryPerformanceReportDaily,
    SearchQueryPerformanceReportHourly,
    UserLocationPerformanceReportDaily,
    UserLocationPerformanceReportHourly,
)
from source_bing_ads.source import SourceBingAds

TEST_CONFIG = {
    "developer_token": "developer_token",
    "client_id": "client_id",
    "refresh_token": "refresh_token",
    "reports_start_date": "2020-01-01T00:00:00Z",
}


class TestClient:
    pass


class TestReport(BingAdsReportingServiceStream, SourceBingAds):
    date_format, report_columns, report_name, cursor_field = "YYYY-MM-DD", None, None, "Time"
    report_aggregation = "Monthly"
    report_schema_name = "campaign_performance_report"

    def __init__(self) -> None:
        self.client = TestClient()


class TestPerformanceReport(BingAdsReportingServicePerformanceStream, SourceBingAds):
    date_format, report_columns, report_name, cursor_field = "YYYY-MM-DD", None, None, "Time"
    report_aggregation = "Monthly"
    report_schema_name = "campaign_performance_report"

    def __init__(self) -> None:
        self.client = TestClient()


def test_get_column_value():
    config = {
        "developer_token": "developer_token",
        "client_id": "client_id",
        "refresh_token": "refresh_token",
        "reports_start_date": "2020-01-01T00:00:00Z",
    }
    test_report = GeographicPerformanceReportDaily(client=Mock(), config=config)

    row_values = _RowValues(
        {"AccountId": 1, "AverageCpc": 3, "AdGroupId": 2, "AccountName": 5, "Spend": 4, "AllRevenue": 6, "Assists": 7},
        {3: "11.5", 1: "33", 2: "--", 5: "123456789", 4: "120.3%", 6: "123,456,789.23", 7: "123,456,789"},
    )
    record = _RowReportRecord(row_values)

    assert test_report.get_column_value(record, "AccountId") == "33"
    assert test_report.get_column_value(record, "AverageCpc") == "11.5"
    assert test_report.get_column_value(record, "AdGroupId") is None
    assert test_report.get_column_value(record, "AccountName") == "123456789"
    assert test_report.get_column_value(record, "Spend") == "120.3"
    assert test_report.get_column_value(record, "AllRevenue") == "123456789.23"
    assert test_report.get_column_value(record, "Assists") == "123456789"


def test_get_updated_state_init_state():
    test_report = TestReport()
    stream_state = {}
    latest_record = {"AccountId": 123, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(stream_state, latest_record)
    assert new_state["123"]["Time"] == "2020-01-02"


def test_get_updated_state_new_state():
    test_report = TestReport()
    stream_state = {"123": {"Time": "2020-01-01"}}
    latest_record = {"AccountId": 123, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(stream_state, latest_record)
    assert new_state["123"]["Time"] == "2020-01-02"


def test_get_updated_state_state_unchanged():
    test_report = TestReport()
    stream_state = {"123": {"Time": "2020-01-03"}}
    latest_record = {"AccountId": 123, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(copy.deepcopy(stream_state), latest_record)
    assert stream_state == new_state


def test_get_updated_state_state_new_account():
    test_report = TestReport()
    stream_state = {"123": {"Time": "2020-01-03"}}
    latest_record = {"AccountId": 234, "Time": "2020-01-02"}
    new_state = test_report.get_updated_state(stream_state, latest_record)
    assert "234" in new_state and "123" in new_state
    assert new_state["234"]["Time"] == "2020-01-02"


@pytest.mark.parametrize(
    "stream_report_daily_cls",
    (
        AccountImpressionPerformanceReportDaily,
        AccountPerformanceReportDaily,
        AdGroupImpressionPerformanceReportDaily,
        AdGroupPerformanceReportDaily,
        AgeGenderAudienceReportDaily,
        AdPerformanceReportDaily,
        CampaignImpressionPerformanceReportDaily,
        CampaignPerformanceReportDaily,
        KeywordPerformanceReportDaily,
        SearchQueryPerformanceReportDaily,
        UserLocationPerformanceReportDaily,
        GeographicPerformanceReportDaily,
    ),
)
def test_get_report_record_timestamp_daily(stream_report_daily_cls):
    stream_report = stream_report_daily_cls(client=Mock(), config=TEST_CONFIG)
    assert "2020-01-01" == stream_report.get_report_record_timestamp("2020-01-01")


def test_get_report_record_timestamp_without_aggregation():
    stream_report = BudgetSummaryReport(client=Mock(), config=TEST_CONFIG)
    assert "2020-07-20" == stream_report.get_report_record_timestamp("7/20/2020")


@pytest.mark.parametrize(
    "stream_report_hourly_cls",
    (
        AccountImpressionPerformanceReportHourly,
        AccountPerformanceReportHourly,
        AdGroupImpressionPerformanceReportHourly,
        AdGroupPerformanceReportHourly,
        AgeGenderAudienceReportHourly,
        AdPerformanceReportHourly,
        CampaignImpressionPerformanceReportHourly,
        CampaignPerformanceReportHourly,
        KeywordPerformanceReportHourly,
        SearchQueryPerformanceReportHourly,
        UserLocationPerformanceReportHourly,
        GeographicPerformanceReportHourly,
    ),
)
def test_get_report_record_timestamp_hourly(stream_report_hourly_cls):
    stream_report = stream_report_hourly_cls(client=Mock(), config=TEST_CONFIG)
    assert "2020-01-01T15:00:00+00:00" == stream_report.get_report_record_timestamp("2020-01-01|15")


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
    stream_state = {"123": {"cursor_field": "2023-04-17T21:29:57+00:00"}}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_performance_report_with_stream_state():
    expected_start_date = pendulum.parse("2023-04-07T21:29:57")
    test_report = TestPerformanceReport()
    test_report.cursor_field = "cursor_field"
    test_report.config = {"lookback_window": 10}
    stream_state = {"123": {"cursor_field": "2023-04-17T21:29:57+00:00"}}
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


@pytest.mark.parametrize(
    "performance_report_cls",
    (
        GeographicPerformanceReportDaily,
        GeographicPerformanceReportHourly,
        GeographicPerformanceReportMonthly,
        GeographicPerformanceReportWeekly,
    ),
)
def test_geographic_performance_report_pk(performance_report_cls):
    stream = performance_report_cls(client=Mock(), config=TEST_CONFIG)
    assert stream.primary_key is None
