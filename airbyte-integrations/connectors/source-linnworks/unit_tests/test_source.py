#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock

import pytest
from source_linnworks.source import SourceLinnworks, LinnworksAuthenticator


@pytest.fixture
def config():
    return {"config": {"application_id": "xxx", "application_secret": "yyy", "token": "zzz", "start_date": "2021-11-01"}}

@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (
            {
                "Token": "00000000-0000-0000-0000-000000000000",
                "Server": "https://xx-ext.linnworks.net",
            },
            (True, None),
        ),
        (
            {
                "Code": None,
                "Message": "Invalid application id or application secret",
            },
            (False, "Unable to connect to Linnworks API with the provided credentials - Error while refreshing access token: 'Token'"),
        ),
    ]
)
def test_check_connection(mocker, config, requests_mock, response, expected):
    source = SourceLinnworks()
    logger_mock = MagicMock()
    requests_mock.post(
        "https://api.linnworks.net/api/Auth/AuthorizeByApplication",
        json=response,
    )
    assert source.check_connection(logger_mock, **config) == expected


def test_authenticator_success(mocker, config, requests_mock):
    config = config["config"]
    authenticator = LinnworksAuthenticator(
        token_refresh_endpoint="http://dummy",
        application_id=config["application_id"],
        application_secret=config["application_secret"],
        token=config["token"],
    )
    response = {
        "Token": "00000000-0000-0000-0000-000000000000",
        "Server": "http://xx-ext.dummy",
    }
    requests_mock.post("http://dummy", json=response)

    assert authenticator.get_server() == response["Server"]


def test_authenticator_error(mocker, config, requests_mock):
    config = config["config"]
    authenticator = LinnworksAuthenticator(
        token_refresh_endpoint="http://dummy",
        application_id=config["application_id"],
        application_secret=config["application_secret"],
        token=config["token"],
    )
    response = {
        "Code": None,
        "Message": "Invalid application id or application secret",
    }
    requests_mock.post("http://dummy", json=response)

    with pytest.raises(Exception, match="Error while refreshing access token: 'Token'"):
        authenticator.get_server()


def test_streams(mocker):
    source = SourceLinnworks()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
