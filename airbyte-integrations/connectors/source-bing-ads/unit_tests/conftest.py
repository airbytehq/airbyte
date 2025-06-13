#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import patch

import pytest
from source_bing_ads import SourceBingAds

from airbyte_cdk.test.state_builder import StateBuilder


@pytest.fixture(name="config")
def config_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "lookback_window": 0,
    }


@pytest.fixture(name="config_without_start_date")
def config_without_start_date_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "lookback_window": 0,
    }


@pytest.fixture(name="config_with_account_names")
def config_with_account_names_fixture():
    """Generates streams settings from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "account_names": [{"operator": "Equals", "name": "airbyte"}, {"operator": "Contains", "name": "demo"}],
        "lookback_window": 0,
    }


@pytest.fixture(name="config_with_custom_reports")
def config_with_custom_reports_fixture():
    """Generates streams settings with custom reports from a config file"""
    return {
        "tenant_id": "common",
        "developer_token": "fake_developer_token",
        "refresh_token": "fake_refresh_token",
        "client_id": "fake_client_id",
        "reports_start_date": "2020-01-01",
        "lookback_window": 0,
        "custom_reports": [
            {
                "name": "my test custom report",
                "reporting_object": "DSAAutoTargetPerformanceReport",
                "report_columns": [
                    "AbsoluteTopImpressionRatePercent",
                    "AccountId",
                    "AccountName",
                    "AccountNumber",
                    "AccountStatus",
                    "AdDistribution",
                    "AdGroupId",
                    "AdGroupName",
                    "AdGroupStatus",
                    "AdId",
                    "AllConversionRate",
                    "AllConversions",
                    "AllConversionsQualified",
                    "AllCostPerConversion",
                    "AllReturnOnAdSpend",
                    "AllRevenue",
                ],
                "report_aggregation": "Weekly",
            }
        ],
    }


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_bing_ads.source.logging.Logger")


@pytest.fixture(name="mock_auth_token")
def mock_auth_token_fixture(requests_mock):
    requests_mock.post(
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        status_code=200,
        json={"access_token": "test", "expires_in": "900", "refresh_token": "test"},
    )


def find_stream(stream_name, config, state=None):
    state = StateBuilder().build() if not state else state
    streams = SourceBingAds(catalog=None, config=config, state=state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")
