# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from test_hourly_reports import HourlyReportsTestWithStateChangesAfterMigration, get_state_after_migration
from test_report_stream import TestSuiteReportStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


class TestBaseCustomReport(TestSuiteReportStream):
    stream_name = "custom_report"

    custom_report_aggregation: str = None

    def setUp(self):
        super().setUp()
        if not self.custom_report_aggregation:
            self.skipTest("Skipping TestBaseCustomReport")

    @property
    def _config(self) -> dict[str, Any]:
        return (
            ConfigBuilder()
            .with_reports_start_date(self.start_date)
            .with_custom_reports(
                [
                    {
                        "name": self.stream_name,
                        "reporting_object": "AgeGenderAudienceReportRequest",
                        "report_columns": [
                            "AccountName",
                            "AccountNumber",
                            "AccountId",
                            "TimePeriod",
                            "CampaignName",
                            "CampaignId",
                            "AdGroupName",
                            "AdGroupId",
                            "AdDistribution",
                            "AgeGroup",
                            "Gender",
                            "Impressions",
                            "Clicks",
                            "Conversions",
                            "Spend",
                            "Revenue",
                            "ExtendedCost",
                            "Assists",
                            "Language",
                            "AccountStatus",
                            "CampaignStatus",
                            "AdGroupStatus",
                            "BaseCampaignId",
                            "AllConversions",
                            "AllRevenue",
                            "ViewThroughConversions",
                            "Goal",
                            "GoalType",
                            "AbsoluteTopImpressionRatePercent",
                            "TopImpressionRatePercent",
                            "ConversionsQualified",
                            "AllConversionsQualified",
                            "ViewThroughConversionsQualified",
                            "ViewThroughRevenue",
                        ],
                        "report_aggregation": self.custom_report_aggregation,
                    }
                ]
            )
            .build()
        )

    def _mock_report_apis(self):
        pass

    def mock_base_requests(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )

    def mock_report_apis(self):
        self.mock_base_requests()
        self._mock_report_apis()


class TestCustomReportDaily(TestBaseCustomReport):
    custom_report_aggregation = "Daily"

    report_file = "custom_report"
    incremental_report_file = "custom_report_incremental"
    records_number = 8

    report_file_with_records_further_start_date = "custom_report_with_record_further_start_date"
    incremental_report_file_with_records_further_cursor = "custom_report_incremental_with_records_further_cursor"

    state_file = "custom_report"
    state_file_legacy = "custom_report"
    state_file_after_migration = "non_hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "non_hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )

    first_read_state = get_state_after_migration(time_period="2024-05-17", account_id=TestSuiteReportStream.account_id)
    second_read_state = get_state_after_migration(time_period="2023-12-25", account_id=TestSuiteReportStream.account_id)
    first_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-17", account_id=TestSuiteReportStream.account_id
    )
    second_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-07", account_id=TestSuiteReportStream.account_id
    )
    second_read_state_for_records_before_start_date = get_state_after_migration(
        time_period="2024-01-01", account_id=TestSuiteReportStream.account_id
    )

    def _mock_report_apis(self):
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )


class TestCustomReportHourly(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "custom_report"
    report_file = "custom_report_hourly"
    records_number = 8
    state_file = "hourly_reports_state"
    incremental_report_file = "custom_report_hourly_incremental"

    report_file_with_records_further_start_date = "custom_hourly_with_record_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    incremental_report_file_with_records_further_cursor = "custom_report_hourly_incremental_with_records_further_cursor"

    custom_report_aggregation = "Hourly"

    @property
    def _config(self) -> dict[str, Any]:
        return (
            ConfigBuilder()
            .with_reports_start_date(self.start_date)
            .with_custom_reports(
                [
                    {
                        "name": self.stream_name,
                        "reporting_object": "AgeGenderAudienceReportRequest",
                        "report_columns": [
                            "AccountName",
                            "AccountNumber",
                            "AccountId",
                            "TimePeriod",
                            "CampaignName",
                            "CampaignId",
                            "AdGroupName",
                            "AdGroupId",
                            "AdDistribution",
                            "AgeGroup",
                            "Gender",
                            "Impressions",
                            "Clicks",
                            "Conversions",
                            "Spend",
                            "Revenue",
                            "ExtendedCost",
                            "Assists",
                            "Language",
                            "AccountStatus",
                            "CampaignStatus",
                            "AdGroupStatus",
                            "BaseCampaignId",
                            "AllConversions",
                            "AllRevenue",
                            "ViewThroughConversions",
                            "Goal",
                            "GoalType",
                            "AbsoluteTopImpressionRatePercent",
                            "TopImpressionRatePercent",
                            "ConversionsQualified",
                            "AllConversionsQualified",
                            "ViewThroughConversionsQualified",
                            "ViewThroughRevenue",
                        ],
                        "report_aggregation": self.custom_report_aggregation,
                    }
                ]
            )
            .build()
        )

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class CustomReportSummary(BaseTest):
    start_date = "2024-01-01"

    stream_name = "custom_report"
    records_number = 8
    report_file = "custom_report_summary"
    custom_report_aggregation = "Summary"

    @property
    def _config(self) -> dict[str, Any]:
        return (
            ConfigBuilder()
            .with_reports_start_date(self.start_date)
            .with_custom_reports(
                [
                    {
                        "name": self.stream_name,
                        "reporting_object": "AgeGenderAudienceReportRequest",
                        "report_columns": [
                            "AccountName",
                            "AccountNumber",
                            "AccountId",
                            "CampaignName",
                            "CampaignId",
                            "AdGroupName",
                            "AdGroupId",
                            "AdDistribution",
                            "AgeGroup",
                            "Gender",
                            "Impressions",
                            "Clicks",
                            "Conversions",
                            "Spend",
                            "Revenue",
                            "ExtendedCost",
                            "Assists",
                            "Language",
                            "AccountStatus",
                            "CampaignStatus",
                            "AdGroupStatus",
                            "BaseCampaignId",
                            "AllConversions",
                            "AllRevenue",
                            "ViewThroughConversions",
                            "Goal",
                            "GoalType",
                            "AbsoluteTopImpressionRatePercent",
                            "TopImpressionRatePercent",
                            "ConversionsQualified",
                            "AllConversionsQualified",
                            "ViewThroughConversionsQualified",
                            "ViewThroughRevenue",
                        ],
                        "report_aggregation": self.custom_report_aggregation,
                    }
                ]
            )
            .build()
        )

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Summary", "Columns": ["AccountName", "AccountNumber", "AccountId", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    @freeze_time("2024-05-06")
    def test_return_records_incrementally_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        # state is not updated as records don't have a cursor field
        assert output.most_recent_state.stream_state.state["TimePeriod"] == self.start_date

    @freeze_time("2024-05-06")
    def test_return_records_incrementally_with_state_from_given_csv_file(self):
        self.mock_report_apis()
        state = StateBuilder().with_stream_state(self.stream_name, {"TimePeriod": self.start_date}).build()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file, state)
        assert len(output.records) == self.records_number
        # state is not updated as records don't have a cursor field
        assert output.most_recent_state.stream_state.state["TimePeriod"] == self.start_date


class CustomReportDayOfWeek(BaseTest):
    start_date = "2024-01-01"

    stream_name = "custom_report"
    records_number = 7
    report_file = "custom_report_day_of_week"
    custom_report_aggregation = "DayOfWeek"

    @property
    def _config(self) -> dict[str, Any]:
        return (
            ConfigBuilder()
            .with_reports_start_date(self.start_date)
            .with_custom_reports(
                [
                    {
                        "name": self.stream_name,
                        "reporting_object": "AgeGenderAudienceReportRequest",
                        "report_columns": [
                            "AccountName",
                            "AccountNumber",
                            "AccountId",
                            "CampaignName",
                            "CampaignId",
                            "AdGroupName",
                            "AdGroupId",
                            "AdDistribution",
                            "AgeGroup",
                            "Gender",
                            "Impressions",
                            "Clicks",
                            "Conversions",
                            "Spend",
                            "Revenue",
                            "ExtendedCost",
                            "Assists",
                            "Language",
                            "AccountStatus",
                            "CampaignStatus",
                            "AdGroupStatus",
                            "BaseCampaignId",
                            "AllConversions",
                            "AllRevenue",
                            "ViewThroughConversions",
                            "Goal",
                            "GoalType",
                            "AbsoluteTopImpressionRatePercent",
                            "TopImpressionRatePercent",
                            "ConversionsQualified",
                            "AllConversionsQualified",
                            "ViewThroughConversionsQualified",
                            "ViewThroughRevenue",
                        ],
                        "report_aggregation": self.custom_report_aggregation,
                    }
                ]
            )
            .build()
        )

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "DayOfWeek", "Columns": ["AccountName", "AccountNumber", "AccountId", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue", "TimePeriod"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file_transform_record(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number
        for record in output.records:
            record = record.record.data
            assert record["TimePeriod"] == "2024-05-06"
            assert record["DayOfWeek"]
            assert record["StartOfTimePeriod"] == self.start_date
            assert record["EndOfTimePeriod"] == "2024-05-06"

    @freeze_time("2024-05-06")
    def test_return_records_incrementally_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        # state is not updated as records don't have a cursor field
        assert output.most_recent_state.stream_state.state["TimePeriod"] == "2024-05-06"

    @freeze_time("2024-05-06")
    def test_return_records_incrementally_with_state_from_given_csv_file(self):
        self.mock_report_apis()
        state = StateBuilder().with_stream_state(self.stream_name, {"TimePeriod": self.start_date}).build()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file, state)
        assert len(output.records) == self.records_number
        # state is not updated as records don't have a cursor field
        assert output.most_recent_state.stream_state.state["TimePeriod"] == "2024-05-06"


class CustomReportHourOfDay(BaseTest):
    start_date = "2024-01-01"

    stream_name = "custom_report"
    records_number = 7
    report_file = "custom_report_hour_of_day"
    custom_report_aggregation = "HourOfDay"

    @property
    def _config(self) -> dict[str, Any]:
        return (
            ConfigBuilder()
            .with_reports_start_date(self.start_date)
            .with_custom_reports(
                [
                    {
                        "name": self.stream_name,
                        "reporting_object": "AgeGenderAudienceReportRequest",
                        "report_columns": [
                            "AccountName",
                            "AccountNumber",
                            "AccountId",
                            "CampaignName",
                            "CampaignId",
                            "AdGroupName",
                            "AdGroupId",
                            "AdDistribution",
                            "AgeGroup",
                            "Gender",
                            "Impressions",
                            "Clicks",
                            "Conversions",
                            "Spend",
                            "Revenue",
                            "ExtendedCost",
                            "Assists",
                            "Language",
                            "AccountStatus",
                            "CampaignStatus",
                            "AdGroupStatus",
                            "BaseCampaignId",
                            "AllConversions",
                            "AllRevenue",
                            "ViewThroughConversions",
                            "Goal",
                            "GoalType",
                            "AbsoluteTopImpressionRatePercent",
                            "TopImpressionRatePercent",
                            "ConversionsQualified",
                            "AllConversionsQualified",
                            "ViewThroughConversionsQualified",
                            "ViewThroughRevenue",
                        ],
                        "report_aggregation": self.custom_report_aggregation,
                    }
                ]
            )
            .build()
        )

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "HourOfDay", "Columns": ["AccountName", "AccountNumber", "AccountId", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue", "TimePeriod"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number

    @freeze_time("2024-05-06")
    def test_return_records_from_given_csv_file_transform_record(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, self.report_file)
        assert len(output.records) == self.records_number
        for record in output.records:
            record = record.record.data
            assert record["TimePeriod"] == "2024-05-06"
            assert record["HourOfDay"]
            assert record["StartOfTimePeriod"] == self.start_date
            assert record["EndOfTimePeriod"] == "2024-05-06"

    @freeze_time("2024-05-06")
    def test_return_records_incrementally_from_given_csv_file(self):
        self.mock_report_apis()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file)
        assert len(output.records) == self.records_number
        # state is not updated as records don't have a cursor field
        assert output.most_recent_state.stream_state.state["TimePeriod"] == "2024-05-06"

    @freeze_time("2024-05-06")
    def test_return_records_incrementally_with_state_from_given_csv_file(self):
        self.mock_report_apis()
        state = StateBuilder().with_stream_state(self.stream_name, {"TimePeriod": self.start_date}).build()
        output = self.read_stream(self.stream_name, SyncMode.incremental, self._config, self.report_file, state)
        assert len(output.records) == self.records_number
        # state is not updated as records don't have a cursor field
        assert output.most_recent_state.stream_state.state["TimePeriod"] == "2024-05-06"
