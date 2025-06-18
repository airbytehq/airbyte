# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_non_hourly_reports import ReportsTestWithStateChangesAfterMigration
from test_hourly_reports import HourlyReportsTestWithStateChangesAfterMigration


class TestAudiencePerformanceReportDailyStream(ReportsTestWithStateChangesAfterMigration):
    stream_name = "audience_performance_report_daily"
    report_file = "audience_performance_report_daily"
    records_number = 8
    incremental_report_file = "audience_performance_report_daily_incremental"
    report_file_with_records_further_start_date = "audience_performance_report_daily_with_records_further_config_start_date"
    incremental_report_file_with_records_further_cursor = "audience_performance_report_daily_incremental_with_records_further_cursor"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AudiencePerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AudiencePerformanceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AudienceId", "AudienceName", "AssociationStatus", "BidAdjustment", "TargetingSetting", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "Revenue", "ReturnOnAdSpend", "RevenuePerConversion", "AccountStatus", "CampaignStatus", "AdGroupStatus", "AudienceType", "BaseCampaignId", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "AssociationId", "AssociationLevel", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AudiencePerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AudiencePerformanceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AudienceId", "AudienceName", "AssociationStatus", "BidAdjustment", "TargetingSetting", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "Revenue", "ReturnOnAdSpend", "RevenuePerConversion", "AccountStatus", "CampaignStatus", "AdGroupStatus", "AudienceType", "BaseCampaignId", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "AssociationId", "AssociationLevel", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 18, "Month": 6, "Year": 2025}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AudiencePerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AudiencePerformanceReportRequest", "Aggregation": "Daily", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AudienceId", "AudienceName", "AssociationStatus", "BidAdjustment", "TargetingSetting", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "Revenue", "ReturnOnAdSpend", "RevenuePerConversion", "AccountStatus", "CampaignStatus", "AdGroupStatus", "AudienceType", "BaseCampaignId", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "AssociationId", "AssociationLevel", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestAudiencePerformanceReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "audience_performance_report_hourly"
    report_file = "audience_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "audience_performance_report_hourly_incremental"
    report_file_with_records_further_start_date = "audience_performance_report_hourly_with_records_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    incremental_report_file_with_records_further_cursor = "audience_performance_report_hourly_incremental_with_records_further_cursor"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AudiencePerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AudiencePerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AudienceId", "AudienceName", "AssociationStatus", "BidAdjustment", "TargetingSetting", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "Revenue", "ReturnOnAdSpend", "RevenuePerConversion", "AccountStatus", "CampaignStatus", "AdGroupStatus", "AudienceType", "BaseCampaignId", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "AssociationId", "AssociationLevel", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AudiencePerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AudiencePerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AudienceId", "AudienceName", "AssociationStatus", "BidAdjustment", "TargetingSetting", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "Revenue", "ReturnOnAdSpend", "RevenuePerConversion", "AccountStatus", "CampaignStatus", "AdGroupStatus", "AudienceType", "BaseCampaignId", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "AssociationId", "AssociationLevel", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AudiencePerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AudiencePerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AudienceId", "AudienceName", "AssociationStatus", "BidAdjustment", "TargetingSetting", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "Revenue", "ReturnOnAdSpend", "RevenuePerConversion", "AccountStatus", "CampaignStatus", "AdGroupStatus", "AudienceType", "BaseCampaignId", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "AssociationId", "AssociationLevel", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )



# class TestAudiencePerformanceReportWeeklyStream(TestSuiteReportStream):
#     stream_name = "audience_performance_report_weekly"
#     report_file = "audience_performance_report_weekly"
#     records_number = 3
#     second_read_records_number = 5
#     state_file = "audience_performance_report_weekly_state"
#     incremental_report_file = "audience_performance_report_weekly_incremental"
#     first_read_state = {"180535609": {"TimePeriod": "2023-12-25"}}
#     second_read_state = {"180535609": {"TimePeriod": "2024-01-29"}}


# class TestAudiencePerformanceReportMonthlyStream(TestSuiteReportStream):
#     stream_name = "audience_performance_report_monthly"
#     report_file = "audience_performance_report_monthly"
#     records_number = 6
#     state_file = "audience_performance_report_monthly_state"
#     incremental_report_file = "audience_performance_report_monthly_incremental"
#     first_read_state = {"180535609": {"TimePeriod": "2023-09-01"}}
#     second_read_state = {"180535609": {"TimePeriod": "2024-03-01"}}
