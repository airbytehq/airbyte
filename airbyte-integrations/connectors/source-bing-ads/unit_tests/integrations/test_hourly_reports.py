# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_report_stream import TestSuiteReportStream

FIRST_STATE = {"180535609": {"TimePeriod": "2023-11-12T00:00:00+00:00"}}
SECOND_STATE = {"180535609": {"TimePeriod": "2023-11-13T00:00:00+00:00"}}


class HourlyReportsTest(TestSuiteReportStream):
    first_read_state = FIRST_STATE
    second_read_state = SECOND_STATE


class TestAgeGenderAudienceReportHourlyStream(HourlyReportsTest):
    stream_name = "age_gender_audience_report_hourly"
    report_file = "age_gender_audience_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "age_gender_audience_report_hourly_incremental"


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


class TestAdPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "ad_performance_report_hourly"
    report_file = "ad_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_performance_report_hourly_incremental"


class TestAdGroupImpressionPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "ad_group_impression_performance_report_hourly"
    report_file = "ad_group_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_group_impression_performance_report_hourly_incremental"


class TestCampaignPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "campaign_performance_report_hourly"
    report_file = "campaign_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "campaign_performance_report_hourly_incremental"


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


class TestAccountPerformanceReportHourlyStream(HourlyReportsTest):
    stream_name = "account_performance_report_hourly"
    report_file = "account_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "account_performance_report_hourly_incremental"
