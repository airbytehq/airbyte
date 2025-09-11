#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from conftest import create_zip_from_csv, find_stream, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


TEST_CONFIG = {
    "developer_token": "developer_token",
    "client_id": "client_id",
    "refresh_token": "refresh_token",
    "reports_start_date": "2020-01-01",
    "tenant_id": "common",
}


@freeze_time("2024-01-01")
@pytest.mark.parametrize(
    "stream_name",
    [
        "ad_performance_report_daily",
        "ad_performance_report_weekly",
        "ad_performance_report_monthly",
        "age_gender_audience_report_daily",
        "age_gender_audience_report_weekly",
        "age_gender_audience_report_monthly",
        "account_impression_performance_report_daily",
        "account_impression_performance_report_weekly",
        "account_impression_performance_report_monthly",
        "account_performance_report_daily",
        "account_performance_report_weekly",
        "account_performance_report_monthly",
        "audience_performance_report_daily",
        "audience_performance_report_weekly",
        "audience_performance_report_monthly",
        "keyword_performance_report_daily",
        "keyword_performance_report_weekly",
        "keyword_performance_report_monthly",
        "ad_group_performance_report_daily",
        "ad_group_performance_report_weekly",
        "ad_group_performance_report_monthly",
        "ad_group_impression_performance_report_daily",
        "ad_group_impression_performance_report_weekly",
        "ad_group_impression_performance_report_monthly",
        "campaign_performance_report_daily",
        "campaign_performance_report_weekly",
        "campaign_performance_report_monthly",
        "campaign_impression_performance_report_daily",
        "campaign_impression_performance_report_weekly",
        "campaign_impression_performance_report_monthly",
        "geographic_performance_report_daily",
        "geographic_performance_report_weekly",
        "geographic_performance_report_monthly",
        "goals_and_funnels_report_daily",
        "goals_and_funnels_report_weekly",
        "goals_and_funnels_report_monthly",
        "product_dimension_performance_report_daily",
        "product_dimension_performance_report_weekly",
        "product_dimension_performance_report_monthly",
        "product_search_query_performance_report_daily",
        "product_search_query_performance_report_weekly",
        "product_search_query_performance_report_monthly",
        "search_query_performance_report_daily",
        "search_query_performance_report_weekly",
        "search_query_performance_report_monthly",
        "user_location_performance_report_daily",
        "user_location_performance_report_weekly",
        "user_location_performance_report_monthly",
    ],
)
def test_get_updated_state_new_state_daily_weekly_monthly(stream_name, mock_auth_token, mock_user_query, mock_account_query, requests_mock):
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
        status_code=200,
        json={"ReportRequestId": "thisisthereport_requestid"},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        status_code=200,
        json={
            "ReportRequestStatus": {
                "Status": "Success",
                "ReportDownloadUrl": "https://bingadsappsstorageprod.blob.core.windows.net:443/download-url",
            }
        },
    )
    requests_mock.get(
        "https://bingadsappsstorageprod.blob.core.windows.net:443/download-url",
        status_code=200,
        content=create_zip_from_csv("report_base_data"),
    )

    stream_state = {"1": {"TimePeriod": "2020-01-01"}}
    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = get_source(TEST_CONFIG, state)
    output = read(source, TEST_CONFIG, catalog, state)

    updated_state = output.most_recent_state.stream_state.state["TimePeriod"]
    assert updated_state == "2023-01-01"


def test_get_report_record_timestamp_without_aggregation(config, mock_user_query, mock_auth_token):
    stream_report = find_stream("budget_summary_report", config)
    record = {"Date": "08/13/2024"}
    expected_record = {"Date": "2024-08-13"}
    transformed_record = list(
        stream_report.retriever.record_selector.filter_and_transform(all_data=[record], stream_state={}, stream_slice={}, records_schema={})
    )[0]
    assert transformed_record["Date"] == expected_record["Date"]


@freeze_time("2024-01-01")
@pytest.mark.parametrize(
    "stream_name",
    (
        "ad_performance_report_hourly",
        "age_gender_audience_report_hourly",
        "account_impression_performance_report_hourly",
        "account_performance_report_hourly",
        "audience_performance_report_hourly",
        "keyword_performance_report_hourly",
        "ad_group_performance_report_hourly",
        "ad_group_impression_performance_report_hourly",
        "campaign_performance_report_hourly",
        "campaign_impression_performance_report_hourly",
        "geographic_performance_report_hourly",
        "goals_and_funnels_report_hourly",
        "product_dimension_performance_report_hourly",
        "product_search_query_performance_report_hourly",
        "search_query_performance_report_hourly",
        "user_location_performance_report_hourly",
    ),
)
def test_get_report_record_timestamp_hourly(stream_name, mock_auth_token, mock_user_query, mock_account_query, requests_mock):
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
        status_code=200,
        json={"ReportRequestId": "thisisthereport_requestid"},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        status_code=200,
        json={
            "ReportRequestStatus": {
                "Status": "Success",
                "ReportDownloadUrl": "https://bingadsappsstorageprod.blob.core.windows.net:443/download-url",
            }
        },
    )
    requests_mock.get(
        "https://bingadsappsstorageprod.blob.core.windows.net:443/download-url",
        status_code=200,
        content=create_zip_from_csv("report_base_data_hourly"),
    )
    stream_state = {"1": {"TimePeriod": "2020-01-01T10:00:00+00:00"}}
    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = get_source(TEST_CONFIG, state)
    output = read(source, TEST_CONFIG, catalog, state)
    assert "2023-01-01T15:00:00+00:00" == output.records[0].record.data["TimePeriod"]


@pytest.mark.parametrize(
    "test_name,config,custom_report_config,expected_name",
    [
        (
            "camel_case_conversion_enabled_by_default",
            {},  # Default config with no disable flag at custom report level
            {"name": "MyCustomReport"},
            "my_custom_report",
        ),
        (
            "camel_case_conversion_enabled_explicitly",
            {},
            {"name": "CampaignPerformanceDaily", "disable_custom_report_names_camel_to_snake_conversion": False},
            "campaign_performance_daily",
        ),
        (
            "camel_case_conversion_disabled",
            {},
            {"name": "MyExactReportName", "disable_custom_report_names_camel_to_snake_conversion": True},
            "MyExactReportName",
        ),
        (
            "snake_case_unchanged_when_enabled",
            {},
            {"name": "already_snake_case"},
            "already_snake_case",
        ),
        (
            "snake_case_unchanged_when_disabled",
            {},
            {"name": "already_snake_case", "disable_custom_report_names_camel_to_snake_conversion": True},
            "already_snake_case",
        ),
        (
            "complex_camel_case_conversion_enabled",
            {},
            {"name": "MyVeryComplexReportNameWithManyWords"},
            "my_very_complex_report_name_with_many_words",
        ),
        (
            "complex_camel_case_conversion_disabled",
            {},
            {"name": "MyVeryComplexReportNameWithManyWords", "disable_custom_report_names_camel_to_snake_conversion": True},
            "MyVeryComplexReportNameWithManyWords",
        ),
        (
            "single_word_unchanged",
            {},
            {"name": "report"},
            "report",
        ),
        (
            "single_capital_word_converted",
            {},
            {"name": "Report"},
            "report",
        ),
        (
            "single_capital_word_unchanged_when_disabled",
            {},
            {"name": "Report", "disable_custom_report_names_camel_to_snake_conversion": True},
            "Report",
        ),
    ],
)
def test_custom_report_name_conversion(test_name, config, custom_report_config, expected_name):
    """Test that custom report name conversion works correctly based on configuration."""
    # Base custom report configuration with required fields
    base_custom_report = {
        "reporting_object": "AccountPerformanceReportRequest",
        "report_columns": ["AccountId", "AccountName", "Impressions", "Clicks"],
        "report_aggregation": "Daily",
    }

    # Merge the test-specific config with the base config
    custom_report = {**base_custom_report, **custom_report_config}

    # Create the full config with custom_reports
    full_config = {**TEST_CONFIG, **config, "custom_reports": [custom_report]}

    # Get the source and its streams
    source = get_source(full_config)
    streams = source.streams(config=full_config)

    # Find the custom report stream by checking all stream names
    custom_stream = None
    for stream in streams:
        # Custom report streams should have the expected name
        if stream.name == expected_name:
            custom_stream = stream
            break

    assert (
        custom_stream is not None
    ), f"Expected custom report stream '{expected_name}' not found. Available streams: {[s.name for s in streams]}"
    assert custom_stream.name == expected_name
