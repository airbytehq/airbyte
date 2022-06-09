#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy

import pytest
from airbyte_cdk import AirbyteLogger
from source_mixpanel.source import SourceMixpanel, TokenAuthenticatorBase64
from source_mixpanel.streams import FunnelsList

from .utils import get_url_to_mock, setup_response

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
def test_check_connection(requests_mock, check_connection_url, config, response_code, expect_success, response_json):
    requests_mock.register_uri("GET", check_connection_url, setup_response(response_code, response_json))
    ok, error = SourceMixpanel().check_connection(logger, config)
    assert ok == expect_success and error != expect_success
    expected_error = response_json.get("error")
    if expected_error:
        assert error == expected_error


def test_check_connection_bad_config():
    config = {}
    ok, error = SourceMixpanel().check_connection(logger, config)
    assert not ok and error


def test_check_connection_incomplete(config):
    config.pop("api_secret")
    ok, error = SourceMixpanel().check_connection(logger, config)
    assert not ok and error


def test_streams(config):
    streams = SourceMixpanel().streams(config)
    assert len(streams) == 7


def test_streams_string_date(config):
    config = copy.deepcopy(config)
    config["start_date"] = "2020-01-01"
    config["end_date"] = "2020-01-02"
    streams = SourceMixpanel().streams(config)
    assert len(streams) == 7
