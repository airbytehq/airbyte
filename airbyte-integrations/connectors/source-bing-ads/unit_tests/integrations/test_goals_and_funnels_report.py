# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_report_stream import TestSuiteReportStream


class TestGoalsAndFunnelsReportDailyStream(TestSuiteReportStream):
    stream_name = "goals_and_funnels_report_daily"
    report_file = "goals_and_funnels_report_daily"
    records_number = 8
    state_file = "goals_and_funnels_report_daily_state"
    incremental_report_file = "goals_and_funnels_report_daily_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-12-17"}}
    second_read_state = {"180535609": {"TimePeriod": "2023-12-24"}}


class TestGoalsAndFunnelsReportHourlyStream(TestSuiteReportStream):
    stream_name = "goals_and_funnels_report_hourly"
    report_file = "goals_and_funnels_report_hourly"
    records_number = 24
    state_file = "goals_and_funnels_report_hourly_state"
    incremental_report_file = "goals_and_funnels_report_hourly_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-11-12T00:00:00+00:00"}}
    second_read_state = {"180535609": {"TimePeriod": "2023-11-13T00:00:00+00:00"}}


class TestGoalsAndFunnelsReportWeeklyStream(TestSuiteReportStream):
    stream_name = "goals_and_funnels_report_weekly"
    report_file = "goals_and_funnels_report_weekly"
    records_number = 3
    second_read_records_number = 5
    state_file = "goals_and_funnels_report_weekly_state"
    incremental_report_file = "goals_and_funnels_report_weekly_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-12-25"}}
    second_read_state = {"180535609": {"TimePeriod": "2024-01-29"}}


class TestGoalsAndFunnelsReportMonthlyStream(TestSuiteReportStream):
    stream_name = "goals_and_funnels_report_monthly"
    report_file = "goals_and_funnels_report_monthly"
    records_number = 6
    state_file = "goals_and_funnels_report_monthly_state"
    incremental_report_file = "goals_and_funnels_report_monthly_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-09-01"}}
    second_read_state = {"180535609": {"TimePeriod": "2024-03-01"}}
