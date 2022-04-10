import pytest
from airbyte_cdk import AirbyteLogger

from source_mixpanel.source import SourceMixpanel

logger = AirbyteLogger()

MIXPANEL_BASE_URL = "https://mixpanel.com/api/2.0/"


def test_check_connection(requests_mock, config, empty_response_ok):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels/list", empty_response_ok)

    ok, error = SourceMixpanel().check_connection(logger, config)

    assert ok and not error


def test_check_connection_bad_request(requests_mock, config, empty_response_bad):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels/list", empty_response_bad)

    ok, error = SourceMixpanel().check_connection(logger, config)

    assert not ok and error


def test_check_connection_empty():
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


@pytest.fixture
def empty_response_ok():
    return setup_response(200, {})


@pytest.fixture
def empty_response_bad():
    return setup_response(400, {})


def setup_response(status, body):
    return [
        {
            "json": body,
            "status_code": status
        }
    ]
