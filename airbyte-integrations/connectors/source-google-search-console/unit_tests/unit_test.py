#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus

import pytest
import requests
from pytest_lazy_fixtures import lf as lazy_fixture
from source_google_search_console.source import SourceGoogleSearchConsole
from source_google_search_console.streams import (
    ROW_LIMIT,
    GoogleSearchConsole,
    QueryAggregationType,
    SearchAnalyticsByCustomDimensions,
    SearchAnalyticsKeywordSiteReportBySite,
)
from utils import command_check

from airbyte_cdk.models import AirbyteConnectionStatus, Status, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


logger = logging.getLogger("airbyte")


class MockResponse:
    def __init__(self, data_field: str, count: int):
        self.value = {data_field: [0 for i in range(count)]}

    def json(self):
        return self.value


def test_bad_aggregation_type_should_retry(requests_mock, bad_aggregation_type):
    stream = SearchAnalyticsKeywordSiteReportBySite(None, ["https://example.com"], "2021-01-01", "2021-01-02")
    requests_mock.post(
        f"{stream.url_base}sites/{stream._site_urls[0]}/searchAnalytics/query", status_code=200, json={"rows": [{"keys": ["TPF_QA"]}]}
    )
    slice = list(stream.stream_slices(None))[0]
    url = stream.url_base + stream.path(None, slice)
    requests_mock.get(url, status_code=400, json=bad_aggregation_type)
    test_response = requests.get(url)
    # before should_retry, the aggregation_type should be set to `by_propety`
    assert stream.aggregation_type == QueryAggregationType.by_property
    # trigger should retry
    assert stream.should_retry(test_response) is False
    # after should_retry, the aggregation_type should be set to `auto`
    assert stream.aggregation_type == QueryAggregationType.auto
    assert stream.raise_on_http_errors is False


@patch.multiple(GoogleSearchConsole, __abstractmethods__=set())
def test_parse_response():
    stream_class = GoogleSearchConsole
    expected = {"keys": ["keys"]}
    stream = stream_class(None, ["https://domain1.com", "https://domain2.com"], "2021-09-01", "2021-09-07")

    stream.data_field = "data_field"
    stream_slice = next(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    response = MagicMock()
    response.json = MagicMock(return_value={"data_field": [{"keys": ["keys"]}]})

    record = next(stream.parse_response(response, stream_state={}, stream_slice=stream_slice))

    assert record == expected


def test_check_connection(config_gen, config, mocker, requests_mock):
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fexample.com%2F", json={})
    requests_mock.get("https://www.googleapis.com/webmasters/v3/sites", json={"siteEntry": [{"siteUrl": "https://example.com/"}]})
    requests_mock.post("https://oauth2.googleapis.com/token", json={"access_token": "token", "expires_in": 10})

    source = SourceGoogleSearchConsole(config=config, catalog=None, state=None)

    assert command_check(source, config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED)

    # test site_urls
    assert command_check(source, config_gen(site_urls=["https://example.com"])) == AirbyteConnectionStatus(status=Status.SUCCEEDED)

    # test start_date
    assert command_check(source, config_gen(start_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config_gen(start_date="")) == AirbyteConnectionStatus(
            status=Status.FAILED,
            message="'' does not match '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'",
        )
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config_gen(start_date="start_date")) == AirbyteConnectionStatus(
            status=Status.FAILED,
            message="'start_date' does not match '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'",
        )

    # test end_date
    assert command_check(source, config_gen(end_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert command_check(source, config_gen(end_date="")) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    with pytest.raises(Exception):
        assert command_check(source, config_gen(end_date="end_date"))

    # test custom_reports
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config_gen(custom_reports_array="")) == AirbyteConnectionStatus(
            status=Status.FAILED,
            message="'<ValidationError: \"{} is not of type \\'array\\'\">'",
        )
    with pytest.raises(AirbyteTracedException):
        assert command_check(source, config_gen(custom_reports_array="{}")) == AirbyteConnectionStatus(
            status=Status.FAILED, message="'<ValidationError: \"{} is not of type \\'array\\'\">'"
        )


@pytest.mark.parametrize(
    "test_config, expected",
    [
        (
            lazy_fixture("config"),
            (
                False,
                "Encountered an error while checking availability of stream sites. Error: 401 Client Error: None for url: https://oauth2.googleapis.com/token",
            ),
        ),
        (
            lazy_fixture("service_account_config"),
            (
                False,
                "Encountered an error while checking availability of stream sites. Error: Error while refreshing access token: Failed to sign token: Could not parse the provided public key.",
            ),
        ),
    ],
)
def test_unauthorized_creds_exceptions(test_config, expected, requests_mock):
    source = SourceGoogleSearchConsole(config=test_config, catalog=None, state=None)
    requests_mock.post("https://oauth2.googleapis.com/token", status_code=401, json={})
    actual = source.check_connection(logger, test_config)
    assert actual == expected


def test_streams(config_gen):
    config = config_gen()
    source = SourceGoogleSearchConsole(config=config, catalog=None, state=None)
    streams = source.streams(config)
    assert len(streams) == 15
    streams = source.streams(config_gen(custom_reports_array=...))
    assert len(streams) == 14


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
