#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
from pytest_lazy_fixtures import lf as lazy_fixture
from source_google_search_console.source import SourceGoogleSearchConsole

from airbyte_cdk.models import AirbyteConnectionStatus, Status, SyncMode
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .conftest import find_stream
from .utils import command_check


logger = logging.getLogger("airbyte")


class MockResponse:
    def __init__(self, data_field: str, count: int):
        self.value = {data_field: [0 for i in range(count)]}

    def json(self):
        return self.value


@pytest.mark.parametrize(
    "site_urls",
    [["https://example1.com", "https://example2.com"], ["https://example.com"]],
)
@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
@pytest.mark.parametrize("data_state", ["all", "final"])
def test_slice(config_gen, site_urls, sync_mode, data_state):
    # config = {
    #     "start_date": "2021-09-01",
    #     "end_date": "2021-09-07",
    #     "site_urls": site_urls,
    # }
    config = config_gen(site_urls=site_urls, start_date="2021-09-01", end_date="2021-09-07")

    stream = find_stream("search_analytics_by_date", config)

    # search_types = stream.search_types
    search_types = ["web", "news", "image", "video", "discover", "googleNews"]
    stream_slice = stream.stream_slices(sync_mode=sync_mode)

    for site_url in site_urls:
        for search_type in search_types:
            for range_ in [
                {"start_time": "2021-09-01", "end_time": "2021-09-03"},
                {"start_time": "2021-09-04", "end_time": "2021-09-06"},
                {"start_time": "2021-09-07", "end_time": "2021-09-07"},
            ]:
                expected = StreamSlice(
                    cursor_slice={
                        "start_time": range_["start_time"],
                        "end_time": range_["end_time"],
                    },
                    partition={
                        "site_url": site_url + "/",
                        "search_type": search_type,
                    },
                )
                assert next(stream_slice) == expected


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


def test_streams_without_custom_reports(config_gen):
    config = config_gen(custom_reports_array=...)
    source = SourceGoogleSearchConsole(config=config, catalog=None, state=None)
    streams = source.streams(config)
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
    stream = find_stream("custom", custom_report_config)
    schema = stream.get_json_schema()
    assert set(schema["properties"]) == set(schema_props)
    assert set(stream.primary_key) == set(primary_key)
