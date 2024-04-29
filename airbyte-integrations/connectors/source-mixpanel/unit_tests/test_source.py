#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.utils import AirbyteTracedException
from source_mixpanel.source import SourceMixpanel, TokenAuthenticatorBase64
from source_mixpanel.streams import Annotations, CohortMembers, Cohorts, Engage, Export, Funnels, FunnelsList, Revenue

from .utils import command_check, get_url_to_mock, setup_response

logger = AirbyteLogger()


@pytest.fixture
def check_connection_url(config):
    auth = TokenAuthenticatorBase64(token=config["credentials"]["api_secret"])
    annotations = Cohorts(authenticator=auth, **config)
    return get_url_to_mock(annotations)


@pytest.mark.parametrize(
    "response_code,expect_success,response_json",
    [(200, True, {}), (400, False, {"error": "Request error"})],
)
def test_check_connection(requests_mock, check_connection_url, config_raw, response_code, expect_success, response_json):
    requests_mock.register_uri("GET", check_connection_url, setup_response(response_code, response_json))
    ok, error = SourceMixpanel().check_connection(logger, config_raw)
    assert ok == expect_success and error != expect_success
    expected_error = response_json.get("error")
    if expected_error:
        assert error == expected_error


def test_check_connection_all_streams_402_error(requests_mock, check_connection_url, config_raw, config):
    auth = TokenAuthenticatorBase64(token=config["credentials"]["api_secret"])
    requests_mock.register_uri(
        "GET", get_url_to_mock(Cohorts(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "GET", get_url_to_mock(Annotations(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "POST", get_url_to_mock(Engage(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "GET", get_url_to_mock(Export(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "GET", get_url_to_mock(Revenue(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "GET", get_url_to_mock(Funnels(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "GET", get_url_to_mock(FunnelsList(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )
    requests_mock.register_uri(
        "GET", get_url_to_mock(CohortMembers(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )

    ok, error = SourceMixpanel().check_connection(logger, config_raw)
    assert ok is False and error == "Payment required"


def test_check_connection_402_error_on_first_stream(requests_mock, check_connection_url, config, config_raw):
    auth = TokenAuthenticatorBase64(token=config["credentials"]["api_secret"])
    requests_mock.register_uri("GET", get_url_to_mock(Cohorts(authenticator=auth, **config)), setup_response(200, {}))
    requests_mock.register_uri(
        "GET", get_url_to_mock(Annotations(authenticator=auth, **config)), setup_response(402, {"error": "Payment required"})
    )

    ok, error = SourceMixpanel().check_connection(logger, config_raw)
    # assert ok is True
    assert error is None


def test_check_connection_bad_config():
    config = {}
    source = SourceMixpanel()
    with pytest.raises(AirbyteTracedException):
        command_check(source, config)


def test_check_connection_incomplete(config_raw):
    config_raw.pop("credentials")
    source = SourceMixpanel()
    with pytest.raises(AirbyteTracedException):
        command_check(source, config_raw)


def test_streams(requests_mock, config_raw):
    requests_mock.register_uri("POST", "https://mixpanel.com/api/2.0/engage?page_size=1000", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/cohorts/list", setup_response(200, {"id": 123}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/revenue", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/funnels", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/funnels/list", setup_response(200, {"funnel_id": 123, "name": "name"}))
    requests_mock.register_uri(
        "GET",
        "https://data.mixpanel.com/api/2.0/export",
        setup_response(200, {"event": "some event", "properties": {"event": 124, "time": 124124}}),
    )

    streams = SourceMixpanel().streams(config_raw)
    assert len(streams) == 7


def test_streams_string_date(requests_mock, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/cohorts/list", setup_response(200, {"id": 123}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/revenue", setup_response(200, {}))
    requests_mock.register_uri("POST", "https://mixpanel.com/api/2.0/engage", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/funnels/list", setup_response(402, {"error": "Payment required"}))
    requests_mock.register_uri(
        "GET",
        "https://data.mixpanel.com/api/2.0/export",
        setup_response(200, {"event": "some event", "properties": {"event": 124, "time": 124124}}),
    )
    config = copy.deepcopy(config_raw)
    config["start_date"] = "2020-01-01"
    config["end_date"] = "2020-01-02"
    streams = SourceMixpanel().streams(config)
    assert len(streams) == 6


def test_streams_disabled_402(requests_mock, config_raw):
    json_response = {"error": "Your plan does not allow API calls. Upgrade at mixpanel.com/pricing"}
    requests_mock.register_uri("POST", "https://mixpanel.com/api/2.0/engage?page_size=1000", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/annotations", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/cohorts/list", setup_response(402, json_response))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/revenue", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/funnels/list", setup_response(402, json_response))
    requests_mock.register_uri(
        "GET", "https://data.mixpanel.com/api/2.0/export?from_date=2017-01-20&to_date=2017-02-18", setup_response(402, json_response)
    )
    streams = SourceMixpanel().streams(config_raw)
    assert {s.name for s in streams} == {"annotations", "engage", "revenue"}


@pytest.mark.parametrize(
    "config, success, expected_error_message",
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
            {"credentials": {"api_secret": "secret"}, "attribution_window": "20 days"},
            False,
            "Please provide a valid integer for the `Attribution window` parameter.",
        ),
        (
            {"credentials": {"api_secret": "secret"}, "select_properties_by_default": "Yes"},
            False,
            "Please provide a valid True/False value for the `Select properties by default` parameter.",
        ),
        ({"credentials": {"api_secret": "secret"}, "region": "UK"}, False, "Region must be either EU or US."),
        (
            {"credentials": {"api_secret": "secret"}, "date_window_size": "month"},
            False,
            "Please provide a valid integer for the `Date slicing window` parameter.",
        ),
        (
            {"credentials": {"username": "user", "secret": "secret"}},
            False,
            "Required parameter 'project_id' missing or malformed. Please provide a valid project ID.",
        ),
        ({"credentials": {"api_secret": "secret"}}, True, None),
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
            },
            True,
            None,
        ),
    ),
)
def test_config_validation(config, success, expected_error_message, requests_mock):
    requests_mock.get("https://mixpanel.com/api/2.0/cohorts/list", status_code=200, json={})
    requests_mock.get("https://eu.mixpanel.com/api/2.0/cohorts/list", status_code=200, json={})
    try:
        is_success, message = SourceMixpanel().check_connection(None, config)
    except AirbyteTracedException as e:
        is_success = False
        message = e.message

    assert is_success is success
    if not is_success:
        assert message == expected_error_message
