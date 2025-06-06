#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock, patch

import pytest
import requests
from pytest_lazy_fixtures import lf as lazy_fixture
from source_google_search_console.source import SourceGoogleSearchConsole
from source_google_search_console.streams import (
    SearchAnalyticsByCustomDimensions,
)

from airbyte_cdk.models import Status

@pytest.mark.parametrize(
    "dimensions, expected_status, schema_props, primary_key",
    (
        (["impressions"], Status.FAILED, None, None),
        (
            [],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type"],
            ["date", "site_url", "search_type"],
        ),
        (
            ["date"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type"],
            ["date", "site_url", "search_type"],
        ),
        (
            ["country", "device", "page", "query"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type", "country", "device", "page", "query"],
            ["date", "country", "device", "page", "query", "site_url", "search_type"],
        ),
        (
            ["country", "device", "page", "query", "date"],
            Status.SUCCEEDED,
            ["clicks", "ctr", "impressions", "position", "date", "site_url", "search_type", "country", "device", "page", "query"],
            ["date", "country", "device", "page", "query", "site_url", "search_type"],
        ),
    ),
)
def test_custom_streams(config_gen, requests_mock, dimensions, expected_status, schema_props, primary_key):
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fexample.com%2F", json={})
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites", json={"siteEntry": [{"siteUrl": "https://example.com/"}]})
    requests_mock.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 10})
    custom_reports = [{"name": "custom", "dimensions": dimensions}]

    custom_report_config = config_gen(custom_reports_array=custom_reports)
    mock_logger = MagicMock()
    status = (
        SourceGoogleSearchConsole(config=custom_report_config, catalog=None, state=None).check(
            config=custom_report_config, logger=mock_logger
        )
    ).status
    assert status is expected_status
    if status is Status.FAILED:
        return
    stream = SearchAnalyticsByCustomDimensions(dimensions, None, ["https://domain1.com", "https://domain2.com"], "2021-09-01", "2021-09-07")
    schema = stream.get_json_schema()
    assert set(schema["properties"]) == set(schema_props)
    assert set(stream.primary_key) == set(primary_key)
