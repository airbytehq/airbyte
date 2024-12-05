#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import urlparse

import _csv
import pendulum
import pytest
import source_bing_ads
from airbyte_cdk.models import SyncMode
from bingads.service_info import SERVICE_INFO_DICT_V13
from bingads.v13.internal.reporting.row_report import _RowReport
from bingads.v13.internal.reporting.row_report_iterator import _RowReportRecord, _RowValues
from source_bing_ads.base_streams import Accounts
from source_bing_ads.report_streams import (
    AccountImpressionPerformanceReportDaily,
    AccountImpressionPerformanceReportHourly,
    AccountPerformanceReportDaily,
    AccountPerformanceReportHourly,
    AccountPerformanceReportMonthly,
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
from suds import WebFault

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


@patch.object(source_bing_ads.source, "Client")
def test_AccountPerformanceReportMonthly_request_params(mocked_client, config):
    accountperformancereportmonthly = AccountPerformanceReportMonthly(mocked_client, config)
    request_params = accountperformancereportmonthly.request_params(account_id=180278106, stream_slice={"time_period": "ThisYear"})
    del request_params["report_request"]
    assert request_params == {
        "overwrite_result_file": True,
        "result_file_directory": "/tmp",
        "result_file_name": "AccountPerformanceReport",
        "timeout_in_milliseconds": 300000,
    }


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
    test_report = GeographicPerformanceReportDaily(client=Mock(), config=TEST_CONFIG)
    test_report.client.reports_start_date = "2020-01-01"
    stream_state = {}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_with_stream_state():
    expected_start_date = pendulum.parse("2023-04-17T21:29:57")
    test_report = GeographicPerformanceReportDaily(client=Mock(), config=TEST_CONFIG)
    test_report.client.reports_start_date = "2020-01-01"
    stream_state = {"123": {"TimePeriod": "2023-04-17T21:29:57+00:00"}}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_performance_report_with_stream_state():
    expected_start_date = pendulum.parse("2023-04-07T21:29:57")
    test_report = GeographicPerformanceReportDaily(client=Mock(), config=TEST_CONFIG)
    test_report.config = {"lookback_window": 10}
    stream_state = {"123": {"TimePeriod": "2023-04-17T21:29:57+00:00"}}
    account_id = "123"
    assert expected_start_date == test_report.get_start_date(stream_state, account_id)


def test_report_get_start_date_performance_report_wo_stream_state():
    days_to_subtract = 10
    reports_start_date = pendulum.parse("2021-04-07T00:00:00")
    test_report = GeographicPerformanceReportDaily(client=Mock(), config=TEST_CONFIG)
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


def test_report_parse_response_csv_error(caplog):
    stream_report = AccountPerformanceReportHourly(client=Mock(), config=TEST_CONFIG)
    fake_response = MagicMock()
    fake_response.report_records.__iter__ = MagicMock(side_effect=_csv.Error)
    list(stream_report.parse_response(fake_response))
    assert "CSV report file for stream `account_performance_report_hourly` is broken or cannot be read correctly: , skipping ..." in caplog.messages


@patch.object(source_bing_ads.source, "Client")
def test_custom_report_clear_namespace(mocked_client, config_with_custom_reports, logger_mock):
    custom_report = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)[0]
    assert custom_report._clear_namespace("tns:ReportAggregation") == "ReportAggregation"


@patch.object(source_bing_ads.source, "Client")
def test_custom_report_get_object_columns(mocked_client, config_with_custom_reports, logger_mock):
    reporting_service_mock = MagicMock()
    reporting_service_mock._get_service_info_dict.return_value = SERVICE_INFO_DICT_V13
    mocked_client.get_service.return_value = reporting_service_mock
    mocked_client.environment = "production"

    custom_report = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)[0]

    tree = ET.parse(urlparse(SERVICE_INFO_DICT_V13[("reporting", mocked_client.environment)]).path)
    request_object = tree.find(f".//{{*}}complexType[@name='{custom_report.report_name}Request']")

    assert custom_report._get_object_columns(request_object, tree) == [
        "TimePeriod",
        "AccountId",
        "AccountName",
        "AccountNumber",
        "AccountStatus",
        "CampaignId",
        "CampaignName",
        "CampaignStatus",
        "AdGroupId",
        "AdGroupName",
        "AdGroupStatus",
        "AdDistribution",
        "Language",
        "Network",
        "TopVsOther",
        "DeviceType",
        "DeviceOS",
        "BidStrategyType",
        "TrackingTemplate",
        "CustomParameters",
        "DynamicAdTargetId",
        "DynamicAdTarget",
        "DynamicAdTargetStatus",
        "WebsiteCoverage",
        "Impressions",
        "Clicks",
        "Ctr",
        "AverageCpc",
        "Spend",
        "AveragePosition",
        "Conversions",
        "ConversionRate",
        "CostPerConversion",
        "Assists",
        "Revenue",
        "ReturnOnAdSpend",
        "CostPerAssist",
        "RevenuePerConversion",
        "RevenuePerAssist",
        "AllConversions",
        "AllRevenue",
        "AllConversionRate",
        "AllCostPerConversion",
        "AllReturnOnAdSpend",
        "AllRevenuePerConversion",
        "ViewThroughConversions",
        "Goal",
        "GoalType",
        "AbsoluteTopImpressionRatePercent",
        "TopImpressionRatePercent",
        "AverageCpm",
        "ConversionsQualified",
        "AllConversionsQualified",
        "ViewThroughConversionsQualified",
        "AdId",
        "ViewThroughRevenue",
    ]


@patch.object(source_bing_ads.source, "Client")
def test_custom_report_send_request(mocked_client, config_with_custom_reports, logger_mock, caplog):
    class Fault:
        faultstring = "Invalid Client Data"

    custom_report = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)[0]
    with patch.object(BingAdsReportingServiceStream, "send_request", side_effect=WebFault(fault=Fault(), document=None)):
        custom_report.send_request(params={}, customer_id="13131313", account_id="800800808")
        assert (
            "Could not sync custom report my test custom report: Please validate your column and aggregation configuration. "
            "Error form server: [Invalid Client Data]"
        ) in caplog.text


@pytest.mark.parametrize(
    "aggregation, datastring, expected",
    [
        (
            "Summary",
            "11/13/2023",
            "2023-11-13",
        ),
        (
            "Hourly",
            "2022-11-13|10",
            "2022-11-13T10:00:00+00:00",
        ),
        (
            "Daily",
            "2022-11-13",
            "2022-11-13",
        ),
        (
            "Weekly",
            "2022-11-13",
            "2022-11-13",
        ),
        (
            "Monthly",
            "2022-11-13",
            "2022-11-13",
        ),
        (
            "WeeklyStartingMonday",
            "2022-11-13",
            "2022-11-13",
        ),
    ],
)
@patch.object(source_bing_ads.source, "Client")
def test_custom_report_get_report_record_timestamp(mocked_client, config_with_custom_reports, aggregation, datastring, expected):
    custom_report = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)[0]
    custom_report.report_aggregation = aggregation
    assert custom_report.get_report_record_timestamp(datastring) == expected


@patch.object(source_bing_ads.source, "Client")
def test_account_performance_report_monthly_stream_slices(mocked_client, config_without_start_date):
    mocked_client.reports_start_date = None
    account_performance_report_monthly = AccountPerformanceReportMonthly(mocked_client, config_without_start_date)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        stream_slice = list(account_performance_report_monthly.stream_slices(sync_mode=SyncMode.full_refresh))
        assert stream_slice == [
            {'account_id': 180519267, 'customer_id': 100, 'time_period': 'LastYear'},
            {'account_id': 180519267, 'customer_id': 100, 'time_period': 'ThisYear'},
            {'account_id': 180278106, 'customer_id': 200, 'time_period': 'LastYear'},
            {'account_id': 180278106, 'customer_id': 200, 'time_period': 'ThisYear'}
        ]


@patch.object(source_bing_ads.source, "Client")
def test_account_performance_report_monthly_stream_slices_no_time_period(mocked_client, config):
    account_performance_report_monthly = AccountPerformanceReportMonthly(mocked_client, config)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        stream_slice = list(account_performance_report_monthly.stream_slices(sync_mode=SyncMode.full_refresh))
        assert stream_slice == [
            {'account_id': 180519267, 'customer_id': 100},
            {'account_id': 180278106, 'customer_id': 200}
        ]


@pytest.mark.parametrize(
    "aggregation",
    [
        "DayOfWeek",
        "HourOfDay",
    ],
)
@patch.object(source_bing_ads.source, "Client")
def test_custom_performance_report_no_last_year_stream_slices(mocked_client, config_with_custom_reports, aggregation):
    mocked_client.reports_start_date = None  # in case of start date time period won't be used in request params
    custom_report = SourceBingAds().get_custom_reports(config_with_custom_reports, mocked_client)[0]
    custom_report.report_aggregation = aggregation
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        stream_slice = list(custom_report.stream_slices(sync_mode=SyncMode.full_refresh))
        assert stream_slice == [
            {"account_id": 180519267, "customer_id": 100, "time_period": "ThisYear"},
            {"account_id": 180278106, "customer_id": 200, "time_period": "ThisYear"},
        ]


@pytest.mark.parametrize(
    "stream, response, records",
    [
        (CampaignPerformanceReportHourly, "hourly_reports/campaign_performance.csv", "hourly_reports/campaign_performance_records.json"),
        (AccountPerformanceReportHourly, "hourly_reports/account_performance.csv", "hourly_reports/account_performance_records.json"),
        (AdGroupPerformanceReportHourly, "hourly_reports/ad_group_performance.csv", "hourly_reports/ad_group_performance_records.json"),
        (AdPerformanceReportHourly, "hourly_reports/ad_performance.csv", "hourly_reports/ad_performance_records.json"),
        (CampaignImpressionPerformanceReportHourly, "hourly_reports/campaign_impression_performance.csv", "hourly_reports/campaign_impression_performance_records.json"),
        (KeywordPerformanceReportHourly, "hourly_reports/keyword_performance.csv", "hourly_reports/keyword_performance_records.json"),
        (GeographicPerformanceReportHourly, "hourly_reports/geographic_performance.csv", "hourly_reports/geographic_performance_records.json"),
        (AgeGenderAudienceReportHourly, "hourly_reports/age_gender_audience.csv", "hourly_reports/age_gender_audience_records.json"),
        (SearchQueryPerformanceReportHourly, "hourly_reports/search_query_performance.csv", "hourly_reports/search_query_performance_records.json"),
        (UserLocationPerformanceReportHourly, "hourly_reports/user_location_performance.csv", "hourly_reports/user_location_performance_records.json"),
        (AccountImpressionPerformanceReportHourly, "hourly_reports/account_impression_performance.csv", "hourly_reports/account_impression_performance_records.json"),
        (AdGroupImpressionPerformanceReportHourly, "hourly_reports/ad_group_impression_performance.csv", "hourly_reports/ad_group_impression_performance_records.json"),
    ],
)
@patch.object(source_bing_ads.source, "Client")
def test_hourly_reports(mocked_client, config, stream, response, records):
    stream_object = stream(mocked_client, config)
    with patch.object(stream, "send_request", return_value=_RowReport(file=Path(__file__).parent / response)):
        with open(Path(__file__).parent / records, "r") as file:
            assert list(stream_object.read_records(sync_mode=SyncMode.full_refresh, stream_slice={}, stream_state={})) == json.load(file)
