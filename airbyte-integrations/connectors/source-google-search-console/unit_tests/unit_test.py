#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus

import pytest
import requests
from airbyte_cdk.models import AirbyteConnectionStatus, Status, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from pytest_lazyfixture import lazy_fixture
from source_google_search_console.source import SourceGoogleSearchConsole
from source_google_search_console.streams import (
    ROW_LIMIT,
    GoogleSearchConsole,
    QueryAggregationType,
    SearchAnalyticsByCustomDimensions,
    SearchAnalyticsByDate,
    SearchAnalyticsKeywordSiteReportBySite,
    Sites,
)
from utils import command_check

logger = logging.getLogger("airbyte")


class MockResponse:
    def __init__(self, data_field: str, count: int):
        self.value = {data_field: [0 for i in range(count)]}

    def json(self):
        return self.value


@pytest.mark.parametrize(
    "count, expected",
    [
        (ROW_LIMIT, ROW_LIMIT),
        (ROW_LIMIT - 1, 0),
        (0, 0),
    ],
)
def test_pagination(count, expected):
    stream = SearchAnalyticsByDate(None, ["https://example.com"], "start_date", "end_date")
    response = MockResponse(stream.data_field, count)
    stream.next_page_token(response)
    assert stream.start_row == expected


@pytest.mark.parametrize(
    "site_urls",
    [["https://example1.com", "https://example2.com"], ["https://example.com"]],
)
@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
@pytest.mark.parametrize("data_state", ["all", "final"])
def test_slice(site_urls, sync_mode, data_state):
    stream = SearchAnalyticsByDate(None, site_urls, "2021-09-01", "2021-09-07")

    search_types = stream.search_types
    stream_slice = stream.stream_slices(sync_mode=sync_mode)

    for site_url in site_urls:
        for search_type in search_types:
            for range_ in [
                {"start_date": "2021-09-01", "end_date": "2021-09-03"},
                {"start_date": "2021-09-04", "end_date": "2021-09-06"},
                {"start_date": "2021-09-07", "end_date": "2021-09-07"},
            ]:
                expected = {
                    "data_state": "final",
                    "site_url": quote_plus(site_url),
                    "search_type": search_type,
                    "start_date": range_["start_date"],
                    "end_date": range_["end_date"],
                }
                assert expected == next(stream_slice)


@pytest.mark.parametrize(
    "current_stream_state, latest_record, expected",
    [
        (
            {"https://example.com": {"web": {"date": "2023-01-01"}}},
            {"site_url": "https://example.com", "search_type": "web", "date": "2021-01-01"},
            {"https://example.com": {"web": {"date": "2023-01-01"}}, "date": "2023-01-01"},
        ),
        (
            {},
            {"site_url": "https://example.com", "search_type": "web", "date": "2021-01-01"},
            {"https://example.com": {"web": {"date": "2021-01-01"}}, "date": "2021-01-01"},
        ),
        (
            {"https://example.com": {"web": {"date": "2021-01-01"}}},
            {"site_url": "https://example.com", "search_type": "web", "date": "2022-01-01"},
            {"https://example.com": {"web": {"date": "2022-01-01"}}, "date": "2022-01-01"},
        ),
    ],
)
def test_state(current_stream_state, latest_record, expected):
    stream = SearchAnalyticsByDate(None, ["https://example.com"], "start_date", "end_date")

    value = stream.get_updated_state(current_stream_state, latest_record)
    assert value == expected


def test_updated_state():
    stream = SearchAnalyticsByDate(None, ["https://domain1.com", "https://domain2.com"], "start_date", "end_date")

    state = {}
    record = {"site_url": "https://domain1.com", "search_type": "web", "date": "2022-01-01"}
    state = stream.get_updated_state(state, record)
    record = {"site_url": "https://domain2.com", "search_type": "web", "date": "2022-01-01"}
    state = stream.get_updated_state(state, record)

    assert state == {
        "https://domain1.com": {"web": {"date": "2022-01-01"}},
        "https://domain2.com": {"web": {"date": "2022-01-01"}},
        "date": "2022-01-01",
    }


def test_forbidden_should_retry(requests_mock, forbidden_error_message_json):
    stream = Sites(None, ["https://domain1.com"], "2023-01-01", "2023-01-01")
    slice = list(stream.stream_slices(None))[0]
    url = stream.url_base + stream.path(None, slice)
    requests_mock.get(url, status_code=403, json=forbidden_error_message_json)
    test_response = requests.get(url)
    assert stream.should_retry(test_response) is False
    assert stream.raise_on_http_errors is False


def test_bad_aggregation_type_should_retry(requests_mock, bad_aggregation_type):
    stream = SearchAnalyticsKeywordSiteReportBySite(None, ["https://example.com"], "2021-01-01", "2021-01-02")
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


@pytest.mark.parametrize(
    "stream_class, expected",
    [
        (
            GoogleSearchConsole,
            {"keys": ["keys"]},
        ),
        (SearchAnalyticsByDate, {"date": "keys", "search_type": "web", "site_url": "https://domain1.com"}),
    ],
)
@patch.multiple(GoogleSearchConsole, __abstractmethods__=set())
def test_parse_response(stream_class, expected):
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

    source = SourceGoogleSearchConsole()

    assert command_check(source, config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED)

    # test site_urls
    assert command_check(source, config_gen(site_urls=["https://example.com"])) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert command_check(source, config_gen(site_urls=["https://missed.com"])) == AirbyteConnectionStatus(
        status=Status.FAILED, message="\"InvalidSiteURLValidationError('The following URLs are not permitted: https://missed.com/')\""
    )

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
    assert command_check(source, config_gen(start_date="2022-99-99")) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="\"Unable to check connectivity to Google Search Console API - ParserError('Unable to parse string [2022-99-99]')\"",
    )

    # test end_date
    assert command_check(source, config_gen(end_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert command_check(source, config_gen(end_date="")) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    with pytest.raises(Exception):
        assert command_check(source, config_gen(end_date="end_date"))
    assert command_check(source, config_gen(end_date="2022-99-99")) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="\"Unable to check connectivity to Google Search Console API - ParserError('Unable to parse string [2022-99-99]')\"",
    )

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
                "UnauthorizedOauthError('Unable to connect with provided OAuth credentials. The `access token` or `refresh token` is expired. Please re-authrenticate using valid account credenials.')",
            ),
        ),
        (
            lazy_fixture("service_account_config"),
            (
                False,
                "UnauthorizedServiceAccountError('Unable to connect with provided Service Account credentials. Make sure the `sevice account credentials` provided are valid.')",
            ),
        ),
    ],
)
def test_unauthorized_creds_exceptions(test_config, expected, requests_mock):
    source = SourceGoogleSearchConsole()
    requests_mock.post("https://oauth2.googleapis.com/token", status_code=401, json={})
    actual = source.check_connection(logger, test_config)
    assert actual == expected


def test_streams(config_gen):
    source = SourceGoogleSearchConsole()
    streams = source.streams(config_gen())
    assert len(streams) == 15
    streams = source.streams(config_gen(custom_reports_array=...))
    assert len(streams) == 14


def test_get_start_date():
    stream = SearchAnalyticsByDate(None, ["https://domain1.com", "https://domain2.com"], "2021-09-01", "2021-09-07")
    date = "2021-09-07"
    state_date = stream._get_start_date(
        stream_state={"https://domain1.com": {"web": {"date": date}}}, site_url="https://domain1.com", search_type="web"
    )

    assert date == str(state_date)


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
    status = SourceGoogleSearchConsole().check(config=config_gen(custom_reports_array=custom_reports), logger=None).status
    assert status is expected_status
    if status is Status.FAILED:
        return
    stream = SearchAnalyticsByCustomDimensions(dimensions, None, ["https://domain1.com", "https://domain2.com"], "2021-09-01", "2021-09-07")
    schema = stream.get_json_schema()
    assert set(schema["properties"]) == set(schema_props)
    assert set(stream.primary_key) == set(primary_key)
