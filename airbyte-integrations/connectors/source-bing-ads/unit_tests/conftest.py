#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import patch

import pytest


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
    return patch("source_bing_ads.source.AirbyteLogger")
