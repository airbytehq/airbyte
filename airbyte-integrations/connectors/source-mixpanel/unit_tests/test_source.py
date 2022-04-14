#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from airbyte_cdk import AirbyteLogger
from source_mixpanel.source import FunnelsList, SourceMixpanel, TokenAuthenticatorBase64

from .utils import setup_response

logger = AirbyteLogger()


@pytest.fixture
def check_connection_url(config):
    auth = TokenAuthenticatorBase64(token=config["api_secret"])
    return FunnelsList(authenticator=auth, **config).path


@pytest.mark.parametrize("response_code,expect_success", [(200, True), (400, False)])
def test_check_connection(requests_mock, check_connection_url, config, response_code, expect_success):
    requests_mock.register_uri("GET", check_connection_url, setup_response(response_code, {}))
    ok, error = SourceMixpanel().check_connection(logger, config)
    assert ok == expect_success and error != expect_success
    if not expect_success:
        assert ok and not error


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
