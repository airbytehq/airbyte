#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi
from source_google_analytics_data_api.api_quota import GoogleAnalyticsApiQuotaBase
from source_google_analytics_data_api.source import GoogleAnalyticsDatApiErrorHandler, MetadataDescriptor
from source_google_analytics_data_api.utils import NO_DIMENSIONS, NO_METRICS, NO_NAME, WRONG_CUSTOM_REPORT_CONFIG, WRONG_JSON_SYNTAX

from airbyte_cdk.models import AirbyteConnectionStatus, FailureType, Status
from airbyte_cdk.sources.streams.http.http import HttpStatusErrorHandler
from airbyte_cdk.utils import AirbyteTracedException


@pytest.mark.parametrize(
    "config_values, is_successful, message",
    [
        ({}, Status.SUCCEEDED, None),
        ({"custom_reports_array": ...}, Status.SUCCEEDED, None),
        ({"custom_reports_array": "[]"}, Status.SUCCEEDED, None),
        ({"custom_reports_array": "invalid"}, Status.FAILED, f"'{WRONG_JSON_SYNTAX}'"),
        ({"custom_reports_array": "{}"}, Status.FAILED, f"'{WRONG_JSON_SYNTAX}'"),
        ({"custom_reports_array": "[{}]"}, Status.FAILED, f"'{NO_NAME}'"),
        ({"custom_reports_array": '[{"name": "name"}]'}, Status.FAILED, f"'{NO_DIMENSIONS}'"),
        ({"custom_reports_array": '[{"name": "daily_active_users", "dimensions": ["date"]}]'}, Status.FAILED, f"'{NO_METRICS}'"),
        (
            {"custom_reports_array": '[{"name": "daily_active_users", "metrics": ["totalUsers"], "dimensions": [{"name": "city"}]}]'},
            Status.FAILED,
            "\"The custom report daily_active_users entered contains invalid dimensions: {'name': 'city'} is not of type 'string'. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).\"",
        ),
        ({"date_ranges_start_date": "2022-20-20"}, Status.FAILED, "\"time data '2022-20-20' does not match format '%Y-%m-%d'\""),
        ({"date_ranges_end_date": "2022-20-20"}, Status.FAILED, "\"time data '2022-20-20' does not match format '%Y-%m-%d'\""),
        (
            {"date_ranges_start_date": "2022-12-20", "date_ranges_end_date": "2022-12-10"},
            Status.FAILED,
            "\"End date '2022-12-10' can not be before start date '2022-12-20'\"",
        ),
        (
            {"credentials": {"auth_type": "Service", "credentials_json": "invalid"}},
            Status.FAILED,
            "'credentials.credentials_json is not valid JSON'",
        ),
        (
            {"custom_reports_array": '[{"name": "name", "dimensions": [], "metrics": []}]'},
            Status.FAILED,
            "'The custom report name entered contains invalid dimensions: [] is too short. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).'",
        ),
        (
            {"custom_reports_array": '[{"name": "daily_active_users", "dimensions": ["date"], "metrics": ["totalUsers"]}]'},
            Status.FAILED,
            "'Custom reports: daily_active_users already exist as a default report(s).'",
        ),
        (
            {"custom_reports_array": '[{"name": "name", "dimensions": ["unknown"], "metrics": ["totalUsers"]}]'},
            Status.FAILED,
            "'The custom report name entered contains invalid dimensions: unknown. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).'",
        ),
        (
            {"custom_reports_array": '[{"name": "name", "dimensions": ["date"], "metrics": ["unknown"]}]'},
            Status.FAILED,
            "'The custom report name entered contains invalid metrics: unknown. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/).'",
        ),
        (
            {
                "custom_reports_array": '[{"name": "pivot_report", "dateRanges": [{ "startDate": "2020-09-01", "endDate": "2020-09-15" }], "dimensions": ["browser", "country", "language"], "metrics": ["sessions"], "pivots": {}}]'
            },
            Status.FAILED,
            "\"The custom report pivot_report entered contains invalid pivots: {} is not of type 'null', 'array'. Ensure the pivot follow the syntax described in the docs (https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot).\"",
        ),
    ],
)
def test_check(requests_mock, config_gen, config_values, is_successful, message):
    requests_mock.register_uri(
        "POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )

    requests_mock.register_uri(
        "GET",
        "https://analyticsdata.googleapis.com/v1beta/properties/108176369/metadata",
        json={
            "dimensions": [{"apiName": "date"}, {"apiName": "country"}, {"apiName": "language"}, {"apiName": "browser"}],
            "metrics": [{"apiName": "totalUsers"}, {"apiName": "screenPageViews"}, {"apiName": "sessions"}],
        },
    )
    requests_mock.register_uri(
        "POST",
        "https://analyticsdata.googleapis.com/v1beta/properties/108176369:runReport",
        json={
            "dimensionHeaders": [{"name": "date"}, {"name": "country"}],
            "metricHeaders": [{"name": "totalUsers", "type": "s"}, {"name": "screenPageViews", "type": "m"}],
            "rows": [],
        },
    )

    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()
    assert source.check(logger, config_gen(**config_values)) == AirbyteConnectionStatus(status=is_successful, message=message)


@pytest.mark.parametrize("error_code", (400, 403))
def test_check_failure_throws_exception(requests_mock, config_gen, error_code):
    requests_mock.register_uri(
        "POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )
    requests_mock.register_uri(
        "GET", "https://analyticsdata.googleapis.com/v1beta/properties/UA-11111111/metadata", json={}, status_code=error_code
    )
    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger, config_gen(property_ids=["UA-11111111"]))
    assert e.value.failure_type == FailureType.config_error
    assert "Access was denied to the property ID entered." in e.value.message


def test_exhausted_quota_recovers_after_two_retries(requests_mock, config_gen):
    """
    If the account runs out of quota the api will return a message asking us to back off for one hour.
    We have set backoff time for this scenario to 30 minutes to check if quota is already recovered, if not
    it will backoff again  30 minutes and quote should be reestablished by then.
    Now, we don't want wait one hour to test out this retry behavior so we will fix time dividing by 600 the quota
    recovery time and also the backoff time.
    """
    requests_mock.register_uri(
        "POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )
    error_response = {
        "error": {
            "message": "Exhausted potentially thresholded requests quota. This quota will refresh in under an hour. To learn more, see"
        }
    }
    requests_mock.register_uri(
        "GET",
        "https://analyticsdata.googleapis.com/v1beta/properties/UA-11111111/metadata",
        # first try we get 429 t=~0
        [
            {"json": error_response, "status_code": 429},
            # first retry we get 429 t=~1800
            {"json": error_response, "status_code": 429},
            # second retry quota is recovered, t=~3600
            {
                "json": {
                    "dimensions": [{"apiName": "date"}, {"apiName": "country"}, {"apiName": "language"}, {"apiName": "browser"}],
                    "metrics": [{"apiName": "totalUsers"}, {"apiName": "screenPageViews"}, {"apiName": "sessions"}],
                },
                "status_code": 200,
            },
        ],
    )

    def fix_time(time):
        return int(time / 600)

    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()
    max_time_fixed = fix_time(GoogleAnalyticsDatApiErrorHandler.QUOTA_RECOVERY_TIME)
    potentially_thresholded_requests_per_hour_mapping = GoogleAnalyticsApiQuotaBase.quota_mapping["potentiallyThresholdedRequestsPerHour"]
    threshold_backoff_time = potentially_thresholded_requests_per_hour_mapping["backoff"]
    fixed_threshold_backoff_time = fix_time(threshold_backoff_time)
    potentially_thresholded_requests_per_hour_mapping_fixed = {
        **potentially_thresholded_requests_per_hour_mapping,
        "backoff": fixed_threshold_backoff_time,
    }
    with (
        patch.object(GoogleAnalyticsDatApiErrorHandler, "QUOTA_RECOVERY_TIME", new=max_time_fixed),
        patch.object(
            GoogleAnalyticsApiQuotaBase,
            "quota_mapping",
            new={
                **GoogleAnalyticsApiQuotaBase.quota_mapping,
                "potentiallyThresholdedRequestsPerHour": potentially_thresholded_requests_per_hour_mapping_fixed,
            },
        ),
    ):
        output = source.check(logger, config_gen(property_ids=["UA-11111111"]))
        assert output == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)


@pytest.mark.parametrize("error_code", (402, 404, 405))
def test_check_failure(requests_mock, config_gen, error_code):
    requests_mock.register_uri(
        "POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )
    requests_mock.register_uri(
        "GET", "https://analyticsdata.googleapis.com/v1beta/properties/UA-11111111/metadata", json={}, status_code=error_code
    )
    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()
    with patch.object(HttpStatusErrorHandler, "max_retries", new=0):
        airbyte_status = source.check(logger, config_gen(property_ids=["UA-11111111"]))
        assert airbyte_status.status == Status.FAILED
        assert airbyte_status.message == repr("Failed to get metadata, over quota, try later")


@pytest.mark.parametrize(
    ("status_code", "response_error_message"),
    (
        (403, "Forbidden for some reason"),
        (400, "Granularity in the cohortsRange is required."),
    ),
)
def test_check_incorrect_custom_reports_config(requests_mock, config_gen, status_code, response_error_message):
    requests_mock.register_uri(
        "POST", "https://oauth2.googleapis.com/token", json={"access_token": "access_token", "expires_in": 3600, "token_type": "Bearer"}
    )
    requests_mock.register_uri(
        "GET",
        "https://analyticsdata.googleapis.com/v1beta/properties/108176369/metadata",
        json={
            "dimensions": [{"apiName": "date"}, {"apiName": "country"}, {"apiName": "language"}, {"apiName": "browser"}],
            "metrics": [{"apiName": "totalUsers"}, {"apiName": "screenPageViews"}, {"apiName": "sessions"}],
        },
    )
    requests_mock.register_uri(
        "POST",
        "https://analyticsdata.googleapis.com/v1beta/properties/108176369:runReport",
        status_code=status_code,
        json={"error": {"message": response_error_message}},
    )
    report_name = "cohort_report"
    config = {"custom_reports_array": f'[{{"name": "{report_name}", "dimensions": ["date"], "metrics": ["totalUsers"]}}]'}
    friendly_message = WRONG_CUSTOM_REPORT_CONFIG.format(report=report_name)
    source = SourceGoogleAnalyticsDataApi()
    logger = MagicMock()
    status, message = source.check_connection(logger, config_gen(**config))
    assert status is False
    assert message == f"{friendly_message} {response_error_message}"


@pytest.mark.parametrize("status_code", (403, 401))
def test_missing_metadata(requests_mock, status_code):
    # required for MetadataDescriptor $instance input
    class TestConfig:
        config = {
            "authenticator": None,
            "property_id": 123,
        }

    # mocking the url for metadata
    requests_mock.register_uri(
        "GET", "https://analyticsdata.googleapis.com/v1beta/properties/123/metadata", json={}, status_code=status_code
    )

    metadata_descriptor = MetadataDescriptor()
    with pytest.raises(AirbyteTracedException) as e:
        metadata_descriptor.__get__(TestConfig(), None)
    assert e.value.failure_type == FailureType.config_error


def test_streams(patch_base_class, config_gen):
    config = config_gen(property_ids=["Prop1", "PropN"])
    source = SourceGoogleAnalyticsDataApi()
    streams = source.streams(config)
    expected_streams_number = 57 * 2
    assert len([stream for stream in streams if "_property_" in stream.name]) == 57
    assert len(set(streams)) == expected_streams_number
