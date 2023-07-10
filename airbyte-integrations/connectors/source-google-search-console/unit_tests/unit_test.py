#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, Status, SyncMode
from source_google_search_console.source import SourceGoogleSearchConsole
from source_google_search_console.streams import ROW_LIMIT, GoogleSearchConsole, SearchAnalyticsByCustomDimensions, SearchAnalyticsByDate
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
    [
        ["https://example1.com", "https://example2.com"], ["https://example.com"]
    ],
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


def test_check_connection(config_gen, mocker, requests_mock):
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
    with pytest.raises(Exception):
        assert command_check(source, config_gen(start_date=...))
    with pytest.raises(Exception):
        assert command_check(source, config_gen(start_date=""))
    with pytest.raises(Exception):
        assert command_check(source, config_gen(start_date="start_date"))
    assert command_check(source, config_gen(start_date="2022-99-99")) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="\"Unable to connect to Google Search Console API with the provided credentials - ParserError('Unable to parse string [2022-99-99]')\"",
    )

    # test end_date
    assert command_check(source, config_gen(end_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert command_check(source, config_gen(end_date="")) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    with pytest.raises(Exception):
        assert command_check(source, config_gen(end_date="end_date"))
    assert command_check(source, config_gen(end_date="2022-99-99")) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="\"Unable to connect to Google Search Console API with the provided credentials - ParserError('Unable to parse string [2022-99-99]')\"",
    )

    # test custom_reports
    assert command_check(source, config_gen(custom_reports="")) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="\"Unable to connect to Google Search Console API with the provided credentials - Exception('custom_reports is not valid JSON')\"",
    )
    assert command_check(source, config_gen(custom_reports="{}")) == AirbyteConnectionStatus(
        status=Status.FAILED, message="'<ValidationError: \"{} is not of type \\'array\\'\">'"
    )


def test_streams(config_gen):
    source = SourceGoogleSearchConsole()
    streams = source.streams(config_gen())
    assert len(streams) == 14
    streams = source.streams(config_gen(custom_reports=...))
    assert len(streams) == 13


def test_get_start_date():
    stream = SearchAnalyticsByDate(None, ["https://domain1.com", "https://domain2.com"], "2021-09-01", "2021-09-07")
    date = "2021-09-07"
    state_date = stream._get_start_date(
        stream_state={"https://domain1.com": {"web": {"date": date}}}, site_url="https://domain1.com", search_type="web"
    )

    assert date == str(state_date)


def test_custom_streams():
    dimensions = ["date", "country"]
    stream = SearchAnalyticsByCustomDimensions(dimensions, None, ["https://domain1.com", "https://domain2.com"], "2021-09-01", "2021-09-07")
    schema = stream.get_json_schema()

    for d in ["clicks", "ctr", "date", "impressions", "position", "search_type", "site_url", "country"]:
        assert d in schema["properties"]
