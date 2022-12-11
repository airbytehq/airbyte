#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from source_mixpanel.source import SourceMixpanel, TokenAuthenticatorBase64
from source_mixpanel.streams import FunnelsList

from .utils import command_check, get_url_to_mock, setup_response

logger = AirbyteLogger()


@pytest.fixture
def check_connection_url(config):
    auth = TokenAuthenticatorBase64(token=config["api_secret"])
    funnel_list = FunnelsList(authenticator=auth, **config)
    return get_url_to_mock(funnel_list)


@pytest.mark.parametrize(
    "response_code,expect_success,response_json",
    [
        (200, True, {}),
        (400, False, {"error": "Request error"}),
        (500, False, {"error": "Server error"}),
    ],
)
def test_check_connection(requests_mock, check_connection_url, config_raw, response_code, expect_success, response_json):
    requests_mock.register_uri("GET", check_connection_url, setup_response(response_code, response_json))
    ok, error = SourceMixpanel().check_connection(logger, config_raw)
    assert ok == expect_success and error != expect_success
    expected_error = response_json.get("error")
    if expected_error:
        assert error == expected_error


def test_check_connection_bad_config():
    config = {}
    source = SourceMixpanel()
    assert command_check(source, config) == AirbyteConnectionStatus(status=Status.FAILED, message="KeyError('api_secret')")


def test_check_connection_incomplete(config_raw):
    config_raw.pop("api_secret")
    source = SourceMixpanel()
    assert command_check(source, config_raw) == AirbyteConnectionStatus(status=Status.FAILED, message="KeyError('api_secret')")


def test_streams(requests_mock, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    streams = SourceMixpanel().streams(config_raw)
    assert len(streams) == 7


def test_streams_string_date(requests_mock, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/properties", setup_response(200, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(200, {}))
    config = copy.deepcopy(config_raw)
    config["start_date"] = "2020-01-01"
    config["end_date"] = "2020-01-02"
    streams = SourceMixpanel().streams(config)
    assert len(streams) == 7


def test_streams_disabled_402(requests_mock, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/engage/properties", setup_response(402, {}))
    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/events/properties/top", setup_response(402, {}))
    streams = SourceMixpanel().streams(config_raw)
    assert {s.name for s in streams} == {"funnels", "revenue", "annotations", "cohorts"}
