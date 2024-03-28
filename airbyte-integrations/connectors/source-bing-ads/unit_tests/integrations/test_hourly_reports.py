# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_report_stream import TestSuiteReportStream

FIRST_STATE = {"180535609": {"TimePeriod": "2023-11-12T00:00:00+00:00"}}
SECOND_STATE = {"180535609": {"TimePeriod": "2023-11-13T00:00:00+00:00"}}


class TestAgeGenderAudienceReportHourlyStream(TestSuiteReportStream):
    stream_name = "age_gender_audience_report_hourly"
    report_file = "age_gender_audience_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "age_gender_audience_report_hourly_incremental"
    first_read_state = {"age_gender_audience_report_hourly": FIRST_STATE}
    second_read_state = {"age_gender_audience_report_hourly": SECOND_STATE}


class TestAccountImpressionPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "account_impression_performance_report_hourly"
    report_file = "account_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "account_impression_performance_report_hourly_incremental"
    first_read_state = {"account_impression_performance_report_hourly": FIRST_STATE}
    second_read_state = {"account_impression_performance_report_hourly": SECOND_STATE}


class TestKeywordPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "keyword_performance_report_hourly"
    report_file = "keyword_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "keyword_performance_report_hourly_incremental"
    first_read_state = {"keyword_performance_report_hourly": FIRST_STATE}
    second_read_state = {"keyword_performance_report_hourly": SECOND_STATE}


class TestAdPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "ad_performance_report_hourly"
    report_file = "ad_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_performance_report_hourly_incremental"
    first_read_state = {"ad_performance_report_hourly": FIRST_STATE}
    second_read_state = {"ad_performance_report_hourly": SECOND_STATE}


class TestAdGroupImpressionPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "ad_group_impression_performance_report_hourly"
    report_file = "ad_group_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_group_impression_performance_report_hourly_incremental"
    first_read_state = {"ad_group_impression_performance_report_hourly": FIRST_STATE}
    second_read_state = {"ad_group_impression_performance_report_hourly": SECOND_STATE}


class TestCampaignPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "campaign_performance_report_hourly"
    report_file = "campaign_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "campaign_performance_report_hourly_incremental"
    first_read_state = {"campaign_performance_report_hourly": FIRST_STATE}
    second_read_state = {"campaign_performance_report_hourly": SECOND_STATE}


class TestCampaignImpressionPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "campaign_impression_performance_report_hourly"
    report_file = "campaign_impression_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "campaign_impression_performance_report_hourly_incremental"
    first_read_state = {"campaign_impression_performance_report_hourly": FIRST_STATE}
    second_read_state = {"campaign_impression_performance_report_hourly": SECOND_STATE}


class TestGeographicPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "geographic_performance_report_hourly"
    report_file = "geographic_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "geographic_performance_report_hourly_incremental"
    first_read_state = {"geographic_performance_report_hourly": FIRST_STATE}
    second_read_state = {"geographic_performance_report_hourly": SECOND_STATE}


class TestSearchQueryPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "search_query_performance_report_hourly"
    report_file = "search_query_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "search_query_performance_report_hourly_incremental"
    first_read_state = {"search_query_performance_report_hourly": FIRST_STATE}
    second_read_state = {"search_query_performance_report_hourly": SECOND_STATE}


class TestUserLocationPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "user_location_performance_report_hourly"
    report_file = "user_location_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "user_location_performance_report_hourly_incremental"
    first_read_state = {"user_location_performance_report_hourly": FIRST_STATE}
    second_read_state = {"user_location_performance_report_hourly": SECOND_STATE}


class TestAdGroupPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "ad_group_performance_report_hourly"
    report_file = "ad_group_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "ad_group_performance_report_hourly_incremental"
    first_read_state = {"ad_group_performance_report_hourly": FIRST_STATE}
    second_read_state = {"ad_group_performance_report_hourly": SECOND_STATE}


class TestAccountPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "account_performance_report_hourly"
    report_file = "account_performance_report_hourly"
    records_number = 24
    state_file = "hourly_reports_state"
    incremental_report_file = "account_performance_report_hourly_incremental"
    first_read_state = {"account_performance_report_hourly": FIRST_STATE}
    second_read_state = {"account_performance_report_hourly": SECOND_STATE}
