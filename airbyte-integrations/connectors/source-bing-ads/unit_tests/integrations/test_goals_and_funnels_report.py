# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_hourly_reports import HourlyReportsTestWithStateChangesAfterMigration
from test_non_hourly_reports import ReportsTestWithStateChangesAfterMigration


class TestGoalsAndFunnelsReportDailyStream(ReportsTestWithStateChangesAfterMigration):
    stream_name = "goals_and_funnels_report_daily"
    report_file = "goals_and_funnels_report_daily"
    records_number = 8
    state_file = "goals_and_funnels_report_daily_state"
    incremental_report_file = "goals_and_funnels_report_daily_incremental"
    report_file_with_records_further_start_date = "goals_and_funnels_report_daily_with_records_further_config_start_date"
    incremental_report_file_with_records_further_start_date = (
        "goals_and_funnels_report_daily_with_records_further_config_start_date_incremental"
    )
    incremental_report_file_with_records_further_cursor = "goals_and_funnels_report_daily_incremental_with_records_further_cursor"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 18, "Month": 6, "Year": 2025}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestGoalsAndFunnelsReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "goals_and_funnels_report_hourly"
    report_file = "goals_and_funnels_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "goals_and_funnels_report_hourly_incremental"
    report_file_with_records_further_start_date = "goals_and_funnels_report_hourly_with_records_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    incremental_report_file_with_records_further_cursor = "goals_and_funnels_report_hourly_incremental_with_records_further_cursor"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestGoalsAndFunnelsReportWeeklyStream(ReportsTestWithStateChangesAfterMigration):
    stream_name = "goals_and_funnels_report_weekly"
    report_file = "goals_and_funnels_report_weekly"
    records_number = 3
    incremental_report_file = "goals_and_funnels_report_weekly_incremental"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Weekly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Weekly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 18, "Month": 6, "Year": 2025}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Weekly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestGoalsAndFunnelsReportMonthlyStream(ReportsTestWithStateChangesAfterMigration):
    stream_name = "goals_and_funnels_report_monthly"
    report_file = "goals_and_funnels_report_monthly"
    records_number = 6
    incremental_report_file = "goals_and_funnels_report_monthly_incremental"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Monthly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Monthly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 18, "Month": 6, "Year": 2025}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "GoalsAndFunnelsReport", "ReturnOnlyCompleteData": false, "Type": "GoalsAndFunnelsReportRequest", "Aggregation": "Monthly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Keyword", "KeywordId", "Goal", "AllConversions", "Assists", "AllRevenue", "GoalId", "DeviceType", "DeviceOS", "AccountStatus", "CampaignStatus", "AdGroupStatus", "KeywordStatus", "GoalType", "ViewThroughConversions", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )
