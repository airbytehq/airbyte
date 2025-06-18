# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_report_stream import TestSuiteReportStream


FIRST_STATE = {"180535609": {"TimePeriod": "2023-11-12T00:00:00+00:00"}}


def get_state_after_migration(time_period: str, account_id: str) -> dict:
    return {
        "lookback_window": 0,
        "parent_state": {},
        "state": {"TimePeriod": f"{time_period}"},
        "states": [
            {
                "cursor": {"TimePeriod": f"{time_period}"},
                "partition": {
                    "account_id": account_id,
                    # "parent_slice": {"parent_slice": {}, "user_id": "123456789"}
                },
            }
        ],
        "use_global_cursor": False,
    }


SECOND_STATE = {"180535609": {"TimePeriod": "2023-11-13T00:00:00+00:00"}}


class HourlyReportsTest(TestSuiteReportStream):
    first_read_state = FIRST_STATE
    second_read_state = SECOND_STATE


class HourlyReportsTestWithStateChangesAfterMigration(TestSuiteReportStream):
    first_read_state = get_state_after_migration(
        time_period=f"{TestSuiteReportStream.start_date}T00:00:00+00:00", account_id=TestSuiteReportStream.account_id
    )
    first_read_state_for_records_further_start_date = get_state_after_migration(
        time_period=f"2024-05-06T01:00:00+00:00", account_id=TestSuiteReportStream.account_id
    )
    second_read_state = SECOND_STATE
    second_read_state_for_records_before_start_date = get_state_after_migration(
        time_period=f"{TestSuiteReportStream.start_date}T00:00:00+00:00", account_id=TestSuiteReportStream.account_id
    )
    second_read_state_for_records_further_start_date = get_state_after_migration(
        time_period="2024-05-07T01:00:00+00:00", account_id=TestSuiteReportStream.account_id
    )

    @property
    def report_file_with_records_further_start_date(self):
        return f"{self.stream_name}_with_records_further_config_start_date"

    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )

    @property
    def incremental_report_file_with_records_further_cursor(self):
        return f"{self.stream_name}_incremental_with_records_further_cursor"


class TestAgeGenderAudienceReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "age_gender_audience_report_hourly"
    report_file = "age_gender_audience_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "age_gender_audience_report_hourly_incremental"
    report_file_with_records_further_start_date = "age_gender_audience_report_hourly_with_record_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    incremental_report_file_with_records_further_cursor = "age_gender_audience_report_hourly_incremental_with_records_further_cursor"

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
        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestAccountImpressionPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "account_impression_performance_report_hourly"
    report_file = "account_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "account_impression_performance_report_hourly_incremental"


class TestKeywordPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "keyword_performance_report_hourly"
    report_file = "keyword_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "keyword_performance_report_hourly_incremental"


class TestAdPerformanceReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "ad_performance_report_hourly"
    report_file = "ad_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_performance_report_hourly_incremental"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AdPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AdPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "CampaignId", "AdGroupId", "AdId", "TimePeriod", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "CurrencyCode", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS", "TopVsOther", "BidMatchType", "DeliveredMatchType", "AccountName", "CampaignName", "CampaignType", "AdGroupName", "Impressions", "Clicks", "Ctr", "Spend", "CostPerConversion", "DestinationUrl", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "FinalAppUrl", "AdDescription", "AdDescription2", "ViewThroughConversions", "ViewThroughConversionsQualified", "AllCostPerConversion", "AllReturnOnAdSpend", "Conversions", "ConversionRate", "ConversionsQualified", "AverageCpc", "AveragePosition", "AverageCpm", "AllConversions", "AllConversionRate", "AllRevenue", "AllRevenuePerConversion", "Revenue", "RevenuePerConversion", "RevenuePerAssist"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AdPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AdPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "CampaignId", "AdGroupId", "AdId", "TimePeriod", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "CurrencyCode", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS", "TopVsOther", "BidMatchType", "DeliveredMatchType", "AccountName", "CampaignName", "CampaignType", "AdGroupName", "Impressions", "Clicks", "Ctr", "Spend", "CostPerConversion", "DestinationUrl", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "FinalAppUrl", "AdDescription", "AdDescription2", "ViewThroughConversions", "ViewThroughConversionsQualified", "AllCostPerConversion", "AllReturnOnAdSpend", "Conversions", "ConversionRate", "ConversionsQualified", "AverageCpc", "AveragePosition", "AverageCpm", "AllConversions", "AllConversionRate", "AllRevenue", "AllRevenuePerConversion", "Revenue", "RevenuePerConversion", "RevenuePerAssist"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestAdGroupImpressionPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "ad_group_impression_performance_report_hourly"
    report_file = "ad_group_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_group_impression_performance_report_hourly_incremental"


class TestCampaignPerformanceReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "campaign_performance_report_hourly"
    report_file = "campaign_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "campaign_performance_report_hourly_incremental"
    report_file_with_records_further_start_date = "campaign_performance_report_hourly_with_records_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
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
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "CampaignPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "CampaignPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "CampaignId", "TimePeriod", "CurrencyCode", "AdDistribution", "DeviceType", "Network", "DeliveredMatchType", "DeviceOS", "TopVsOther", "BidMatchType", "AccountName", "CampaignName", "CampaignType", "CampaignStatus", "CampaignLabels", "Impressions", "Clicks", "Ctr", "Spend", "CostPerConversion", "QualityScore", "AdRelevance", "LandingPageExperience", "PhoneImpressions", "PhoneCalls", "Ptr", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "ViewThroughConversions", "AllCostPerConversion", "AllReturnOnAdSpend", "AllConversions", "ConversionsQualified", "AllConversionRate", "AllRevenue", "AllRevenuePerConversion", "AverageCpc", "AveragePosition", "AverageCpm", "Conversions", "ConversionRate", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualitySophisticatedClicks", "LowQualityConversions", "LowQualityConversionRate", "Revenue", "RevenuePerConversion", "RevenuePerAssist", "BudgetName", "BudgetStatus", "BudgetAssociationStatus"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "CampaignPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "CampaignPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "CampaignId", "TimePeriod", "CurrencyCode", "AdDistribution", "DeviceType", "Network", "DeliveredMatchType", "DeviceOS", "TopVsOther", "BidMatchType", "AccountName", "CampaignName", "CampaignType", "CampaignStatus", "CampaignLabels", "Impressions", "Clicks", "Ctr", "Spend", "CostPerConversion", "QualityScore", "AdRelevance", "LandingPageExperience", "PhoneImpressions", "PhoneCalls", "Ptr", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "ViewThroughConversions", "AllCostPerConversion", "AllReturnOnAdSpend", "AllConversions", "ConversionsQualified", "AllConversionRate", "AllRevenue", "AllRevenuePerConversion", "AverageCpc", "AveragePosition", "AverageCpm", "Conversions", "ConversionRate", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualitySophisticatedClicks", "LowQualityConversions", "LowQualityConversionRate", "Revenue", "RevenuePerConversion", "RevenuePerAssist", "BudgetName", "BudgetStatus", "BudgetAssociationStatus"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )

        # for no config start date test
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "CampaignPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "CampaignPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "CampaignId", "TimePeriod", "CurrencyCode", "AdDistribution", "DeviceType", "Network", "DeliveredMatchType", "DeviceOS", "TopVsOther", "BidMatchType", "AccountName", "CampaignName", "CampaignType", "CampaignStatus", "CampaignLabels", "Impressions", "Clicks", "Ctr", "Spend", "CostPerConversion", "QualityScore", "AdRelevance", "LandingPageExperience", "PhoneImpressions", "PhoneCalls", "Ptr", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "ViewThroughConversions", "AllCostPerConversion", "AllReturnOnAdSpend", "AllConversions", "ConversionsQualified", "AllConversionRate", "AllRevenue", "AllRevenuePerConversion", "AverageCpc", "AveragePosition", "AverageCpm", "Conversions", "ConversionRate", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualitySophisticatedClicks", "LowQualityConversions", "LowQualityConversionRate", "Revenue", "RevenuePerConversion", "RevenuePerAssist", "BudgetName", "BudgetStatus", "BudgetAssociationStatus"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )


class TestCampaignImpressionPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "campaign_impression_performance_report_hourly"
    report_file = "campaign_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "campaign_impression_performance_report_hourly_incremental"


class TestGeographicPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "geographic_performance_report_hourly"
    report_file = "geographic_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "geographic_performance_report_hourly_incremental"


class TestSearchQueryPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "search_query_performance_report_hourly"
    report_file = "search_query_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "search_query_performance_report_hourly_incremental"


class TestUserLocationPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "user_location_performance_report_hourly"
    report_file = "user_location_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "user_location_performance_report_hourly_incremental"


class TestAdGroupPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "ad_group_performance_report_hourly"
    report_file = "ad_group_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_group_performance_report_hourly_incremental"


class TestAccountPerformanceReportHourlyStream(HourlyReportsTestWithStateChangesAfterMigration):
    stream_name = "account_performance_report_hourly"
    report_file = "account_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "account_performance_report_hourly_incremental"
    report_file_with_records_further_start_date = "account_performance_report_hourly_with_records_further_config_start_date"
    state_file_legacy = "hourly_reports_state_legacy"
    state_file_after_migration = "hourly_reports_state_after_migration"
    state_file_after_migration_with_cursor_further_config_start_date = (
        "hourly_reports_state_after_migration_with_cursor_further_config_start_date"
    )
    incremental_report_file_with_records_further_cursor = "account_performance_report_hourly_incremental_with_records_further_cursor"

    def mock_report_apis(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AccountPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AccountPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "TimePeriod", "CurrencyCode", "AdDistribution", "DeviceType", "Network", "DeliveredMatchType", "DeviceOS", "TopVsOther", "BidMatchType", "AccountName", "AccountNumber", "PhoneImpressions", "PhoneCalls", "Clicks", "Ctr", "Spend", "Impressions", "Assists", "ReturnOnAdSpend", "AverageCpc", "AveragePosition", "AverageCpm", "Conversions", "ConversionsQualified", "ConversionRate", "CostPerAssist", "CostPerConversion", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualitySophisticatedClicks", "LowQualityConversions", "LowQualityConversionRate", "Revenue", "RevenuePerAssist", "RevenuePerConversion", "Ptr"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        # for second read
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AccountPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AccountPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "TimePeriod", "CurrencyCode", "AdDistribution", "DeviceType", "Network", "DeliveredMatchType", "DeviceOS", "TopVsOther", "BidMatchType", "AccountName", "AccountNumber", "PhoneImpressions", "PhoneCalls", "Clicks", "Ctr", "Spend", "Impressions", "Assists", "ReturnOnAdSpend", "AverageCpc", "AveragePosition", "AverageCpm", "Conversions", "ConversionsQualified", "ConversionRate", "CostPerAssist", "CostPerConversion", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualitySophisticatedClicks", "LowQualityConversions", "LowQualityConversionRate", "Revenue", "RevenuePerAssist", "RevenuePerConversion", "Ptr"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 6, "Month": 5, "Year": 2024}, "CustomDateRangeEnd": {"Day": 8, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            body=b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AccountPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AccountPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountId", "TimePeriod", "CurrencyCode", "AdDistribution", "DeviceType", "Network", "DeliveredMatchType", "DeviceOS", "TopVsOther", "BidMatchType", "AccountName", "AccountNumber", "PhoneImpressions", "PhoneCalls", "Clicks", "Ctr", "Spend", "Impressions", "Assists", "ReturnOnAdSpend", "AverageCpc", "AveragePosition", "AverageCpm", "Conversions", "ConversionsQualified", "ConversionRate", "CostPerAssist", "CostPerConversion", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualitySophisticatedClicks", "LowQualityConversions", "LowQualityConversionRate", "Revenue", "RevenuePerAssist", "RevenuePerConversion", "Ptr"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2023}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}',
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )
