#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import responses
from unittest.mock import MagicMock

from source_pendo_python.source import SourcePendoPython, PendoAuthenticator


fake_token = 'ABC123'


@pytest.fixture(name="config")
def config_fixture():
    return {"api_key": fake_token}


def test_pendo_authenticator():
    fake_token = 'ABC123'
    authenticator = PendoAuthenticator(fake_token)
    assert authenticator.get_auth_header() == {"X-Pendo-Integration-Key": fake_token}


def test_get_authenticator(config):
    fake_token = 'ABC123'
    auth = SourcePendoPython._get_authenticator(config)
    assert auth._token == PendoAuthenticator(fake_token)._token


@responses.activate
def test_check_connection(config):
    source = SourcePendoPython()
    logger_mock = MagicMock()
    responses.add(
        responses.GET,
        "https://app.pendo.io/api/v1/page",
        json=[],
    )
    ok, error_msg = source.check_connection(logger_mock, config)

    assert ok
    assert not error_msg


def test_check_connection_fail():
    source = SourcePendoPython()
    logger_mock = MagicMock()
    ok, error_msg = source.check_connection(logger_mock, {})

    assert not ok
    assert error_msg


def test_streams(config):
    source = SourcePendoPython()
    streams = source.streams(config)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
