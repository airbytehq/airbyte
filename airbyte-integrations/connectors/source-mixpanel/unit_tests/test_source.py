#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from unittest.mock import MagicMock

import pytest
from source_mixpanel.source import SourceMixpanel

from airbyte_cdk.utils import AirbyteTracedException

from .utils import command_check, get_url_to_mock, init_stream, setup_response


logger = logging.getLogger("airbyte")


@pytest.fixture
def check_connection_url(config_raw):
    export_stream = init_stream("export", config_raw)
    return get_url_to_mock(export_stream)


@pytest.mark.parametrize("response_code,expect_success,response_json", [(400, False, {"error": "Request error"})])
def test_check_connection(requests_mock, check_connection_url, config_raw, response_code, expect_success, response_json):
    # requests_mock.register_uri("GET", check_connection_url, setup_response(response_code, response_json))
    requests_mock.get("https://mixpanel.com/api/query/cohorts/list", status_code=response_code, json=response_json)
    requests_mock.get("https://eu.mixpanel.com/api/query/cohorts/list", status_code=response_code, json=response_json)
    ok, error = SourceMixpanel(MagicMock(), config_raw, MagicMock()).check_connection(logger, config_raw)
    assert ok == expect_success


def test_check_connection_bad_config():
    config = {}
    source = SourceMixpanel(MagicMock(), config, MagicMock())
    with pytest.raises(AirbyteTracedException):
        command_check(source, config)


def test_check_connection_incomplete(config_raw):
    config_raw.pop("credentials")
    source = SourceMixpanel(MagicMock(), config_raw, MagicMock())
    with pytest.raises(AirbyteTracedException):
        command_check(source, config_raw)


def test_streams(requests_mock, config_raw):
    requests_mock.register_uri("POST", "https://mixpanel.com/api/query/engage?page_size=1000", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/cohorts/list", setup_response(200, {"id": 123}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/revenue", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/funnels", setup_response(200, {}))
    requests_mock.register_uri(
        "GET", "https://mixpanel.com/api/query/funnels/list", setup_response(200, {"funnel_id": 123, "name": "name"})
    )
    requests_mock.register_uri(
        "GET",
        "https://data.mixpanel.com/api/2.0/export",
        setup_response(200, {"event": "some event", "properties": {"event": 124, "time": 124124}}),
    )

    streams = SourceMixpanel(MagicMock(), config_raw, MagicMock()).streams(config_raw)
    assert len(streams) == 7


def test_streams_string_date(requests_mock, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/cohorts/list", setup_response(200, {"id": 123}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/revenue", setup_response(200, {}))
    requests_mock.register_uri("POST", "https://mixpanel.com/api/query/engage", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/funnels/list", setup_response(402, {"error": "Payment required"}))
    requests_mock.register_uri(
        "GET",
        "https://data.mixpanel.com/api/2.0/export",
        setup_response(200, {"event": "some event", "properties": {"event": 124, "time": 124124}}),
    )
    config = copy.deepcopy(config_raw)
    config["start_date"] = "2020-01-01"
    config["end_date"] = "2020-01-02"
    streams = SourceMixpanel(MagicMock(), config, MagicMock()).streams(config)
    assert len(streams) == 7


@pytest.mark.parametrize(
    "config, expected_is_success, expected_error_message",
    (
        (
            {"credentials": {"api_secret": "secret"}, "project_timezone": "Miami"},
            False,
            "Could not parse time zone: Miami, please enter a valid timezone.",
        ),
        (
            {"credentials": {"api_secret": "secret"}, "start_date": "20 Jan 2021"},
            False,
            "time data '20 Jan 2021' does not match format '%Y-%m-%dT%H:%M:%SZ'",
        ),
        (
            {"credentials": {"api_secret": "secret"}, "end_date": "20 Jan 2021"},
            False,
            "time data '20 Jan 2021' does not match format '%Y-%m-%dT%H:%M:%SZ'",
        ),
        (
            {"credentials": {"username": "user", "secret": "secret"}},
            False,
            "Required parameter 'project_id' missing or malformed. Please provide a valid project ID.",
        ),
        ({"credentials": {"api_secret": "secret"}, "region": "EU", "start_date": "2021-02-01T00:00:00Z"}, True, None),
        (
            {
                "credentials": {"username": "user", "secret": "secret", "project_id": 2397709},
                "project_timezone": "US/Pacific",
                "start_date": "2021-02-01T00:00:00Z",
                "end_date": "2023-02-01T00:00:00Z",
                "attribution_window": 10,
                "select_properties_by_default": True,
                "region": "EU",
                "date_window_size": 10,
                "page_size": 1000,
            },
            True,
            None,
        ),
    ),
)
def test_config_validation(config, expected_is_success, expected_error_message, requests_mock):
    requests_mock.get(
        "https://eu.mixpanel.com/api/query/engage/revenue?project_id=2397709&from_date=2021-02-01&to_date=2021-02-10",
        status_code=200,
        json=[{}],
    )
    requests_mock.get(
        "https://eu.mixpanel.com/api/query/engage/revenue?from_date=2021-02-01&to_date=2021-03-02", status_code=200, json=[{}]
    )
    try:
        is_success, message = SourceMixpanel(MagicMock(), config, MagicMock()).check_connection(MagicMock(), config)
    except AirbyteTracedException as e:
        is_success = False
        message = e.message

    assert is_success is expected_is_success, f"Actual connection status doesn't match with expected value. Actual error message {message}"
    if not is_success:
        assert expected_error_message in message
