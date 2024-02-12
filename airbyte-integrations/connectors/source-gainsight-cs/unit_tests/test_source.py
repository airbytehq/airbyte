#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import responses
from unittest.mock import MagicMock, patch

from source_gainsight_cs.source import SourceGainsightCs, GainsightCsAuthenticator


GAINSIGHT_DOMAIN_URL = "https://fake-domain.gainsightcloud.com"
FAKE_TOKEN = 'ABC123'
GAINSIGHT_OBJECTS = ["person", "playbook", "gsuer", "company", "custom1", "custom2"]


@pytest.fixture(name="config")
def config_fixture():
    return {"access_key": FAKE_TOKEN, "domain_url": GAINSIGHT_DOMAIN_URL}


@pytest.fixture
def mock_get_objects(mocker):
    mocker.patch.object(SourceGainsightCs, "get_objects", return_value=GAINSIGHT_OBJECTS)


def test_gainsight_cs_authenticator():
    authenticator = GainsightCsAuthenticator(FAKE_TOKEN)
    assert authenticator.get_auth_header() == {"AccessKey": FAKE_TOKEN}


def test_get_authenticator(config):
    auth = SourceGainsightCs._get_authenticator(config)
    assert auth._token == GainsightCsAuthenticator(FAKE_TOKEN)._token


@responses.activate
def test_check_connection(config):
    source = SourceGainsightCs()
    logger_mock = MagicMock()
    responses.add(
        responses.GET,
        f"{GAINSIGHT_DOMAIN_URL}/v1/meta/services/objects/Person/describe?idd=true",
        json=[],
    )
    ok, error_msg = source.check_connection(logger_mock, config)

    assert ok
    assert not error_msg


def test_check_connection_fail():
    source = SourceGainsightCs()
    logger_mock = MagicMock()
    ok, error_msg = source.check_connection(logger_mock, {})

    assert not ok
    assert error_msg


def test_streams(config, mock_get_objects):
    source = SourceGainsightCs()
    streams = source.streams(config)
    expected_streams_number = len(GAINSIGHT_OBJECTS)
    assert len(streams) == expected_streams_number
