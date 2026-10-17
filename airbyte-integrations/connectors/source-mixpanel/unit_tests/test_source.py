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


@pytest.mark.parametrize(
    "selected_streams",
    [
        pytest.param(["export"], id="export_only"),
        pytest.param(["annotations"], id="declarative_stream_only"),
    ],
)
def test_check_connection_with_filtered_catalog(requests_mock, config_raw, selected_streams):
    requests_mock.get("https://mixpanel.com/api/query/cohorts/list", status_code=200, json=[])
    config = {
        **config_raw,
        "start_date": "2024-01-25T00:00:00Z",
        "end_date": "2024-02-25T00:00:00Z",
        "streams": selected_streams,
    }

    ok, error = SourceMixpanel(MagicMock(), config, MagicMock()).check_connection(logger, config)

    assert ok is True
    assert error is None


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
    assert len(streams) == 6
    assert "revenue" not in [stream.name for stream in streams]


@pytest.mark.parametrize(
    "selected_streams,expected_count,expected_names",
    [
        pytest.param(None, 6, None, id="no_filter_returns_all"),
        pytest.param([], 6, None, id="empty_list_returns_all"),
        pytest.param(["cohorts", "annotations"], 2, {"cohorts", "annotations"}, id="subset_filter"),
        pytest.param(["export"], 1, {"export"}, id="single_stream_filter"),
        pytest.param(
            ["cohorts", "engage", "annotations", "cohort_members", "funnels", "export"],
            6,
            {"cohorts", "engage", "annotations", "cohort_members", "funnels", "export"},
            id="all_streams_explicit",
        ),
    ],
)
def test_streams_filtering(requests_mock, config_raw, selected_streams, expected_count, expected_names):
    requests_mock.register_uri("POST", "https://mixpanel.com/api/query/engage?page_size=1000", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/cohorts/list", setup_response(200, {"id": 123}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/funnels", setup_response(200, {}))
    requests_mock.register_uri(
        "GET", "https://mixpanel.com/api/query/funnels/list", setup_response(200, {"funnel_id": 123, "name": "name"})
    )
    requests_mock.register_uri(
        "GET",
        "https://data.mixpanel.com/api/2.0/export",
        setup_response(200, {"event": "some event", "properties": {"event": 124, "time": 124124}}),
    )

    config = copy.deepcopy(config_raw)
    if selected_streams is not None:
        config["streams"] = selected_streams

    streams = SourceMixpanel(MagicMock(), config, MagicMock()).streams(config)
    assert len(streams) == expected_count
    if expected_names:
        assert {s.name for s in streams} == expected_names


@pytest.mark.parametrize(
    "enable_export_raw,selected_streams,expected_names",
    [
        pytest.param(False, ["export"], {"export"}, id="disabled"),
        pytest.param(True, ["export"], {"export"}, id="enabled_but_filtered"),
        pytest.param(True, ["export_raw"], {"export_raw"}, id="enabled_and_selected"),
        pytest.param(
            True, None, {"cohorts", "engage", "annotations", "cohort_members", "funnels", "export", "export_raw"}, id="enabled_all"
        ),
    ],
)
def test_export_raw_stream_selection(requests_mock, config_raw, enable_export_raw, selected_streams, expected_names):
    requests_mock.register_uri("POST", "https://mixpanel.com/api/query/engage?page_size=1000", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/cohorts/list", setup_response(200, {"id": 123}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/funnels", setup_response(200, {}))
    requests_mock.register_uri(
        "GET", "https://mixpanel.com/api/query/funnels/list", setup_response(200, {"funnel_id": 123, "name": "name"})
    )

    config = copy.deepcopy(config_raw)
    config["enable_export_raw"] = enable_export_raw
    if selected_streams is not None:
        config["streams"] = selected_streams

    streams = SourceMixpanel(MagicMock(), config, MagicMock()).streams(config)

    assert {stream.name for stream in streams} == expected_names


def test_streams_string_date(requests_mock, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/cohorts/list", setup_response(200, {"id": 123}))
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
    assert len(streams) == 6


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
            "Could not parse start date: 20 Jan 2021. Please enter a valid start date.",
        ),
        (
            {"credentials": {"api_secret": "secret"}, "end_date": "20 Jan 2021"},
            False,
            "Could not parse end date: 20 Jan 2021. Please enter a valid end date.",
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
    requests_mock.get("https://mixpanel.com/api/query/cohorts/list", status_code=200, json=[{"a": 1, "created": "2021-02-11T00:00:00Z"}])
    requests_mock.get("https://eu.mixpanel.com/api/query/cohorts/list", status_code=200, json=[{"a": 1, "created": "2021-02-11T00:00:00Z"}])

    try:
        is_success, message = SourceMixpanel(MagicMock(), config, MagicMock()).check_connection(MagicMock(), config)
    except AirbyteTracedException as e:
        is_success = False
        message = e.message

    assert is_success is expected_is_success, f"Actual connection status doesn't match with expected value. Actual error message {message}"
    if not is_success:
        assert expected_error_message in message
