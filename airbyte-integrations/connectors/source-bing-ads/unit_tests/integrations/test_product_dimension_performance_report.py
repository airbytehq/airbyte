# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from test_report_stream import TestSuiteReportStream


class TestProductDimensionPerformanceReportDailyStream(TestSuiteReportStream):
    stream_name = "product_dimension_performance_report_daily"
    report_file = "product_dimension_performance_report_daily"
    records_number = 8
    state_file = "product_dimension_performance_report_daily_state"
    incremental_report_file = "product_dimension_performance_report_daily_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-12-17"}}
    second_read_state = {"180535609": {"TimePeriod": "2023-12-25"}}


class TestProductDimensionPerformanceReportHourlyStream(TestSuiteReportStream):
    stream_name = "product_dimension_performance_report_hourly"
    report_file = "product_dimension_performance_report_hourly"
    records_number = 8
    state_file = "product_dimension_performance_report_hourly_state"
    incremental_report_file = "product_dimension_performance_report_hourly_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-11-11T01:00:00+00:00"}}
    second_read_state = {"180535609": {"TimePeriod": "2023-11-12T01:00:00+00:00"}}


class TestProductDimensionPerformanceReportWeeklyStream(TestSuiteReportStream):
    stream_name = "product_dimension_performance_report_weekly"
    report_file = "product_dimension_performance_report_weekly"
    records_number = 8
    state_file = "product_dimension_performance_report_weekly_state"
    incremental_report_file = "product_dimension_performance_report_weekly_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-12-17"}}
    second_read_state = {"180535609": {"TimePeriod": "2023-12-25"}}


class TestProductDimensionPerformanceReportMonthlyStream(TestSuiteReportStream):
    stream_name = "product_dimension_performance_report_monthly"
    report_file = "product_dimension_performance_report_monthly"
    records_number = 8
    state_file = "product_dimension_performance_report_monthly_state"
    incremental_report_file = "product_dimension_performance_report_monthly_incremental"
    first_read_state = {"180535609": {"TimePeriod": "2023-12-01"}}
    second_read_state = {"180535609": {"TimePeriod": "2024-01-01"}}
