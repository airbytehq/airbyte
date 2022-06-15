#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_linnworks.source import LinnworksAuthenticator, SourceLinnworks


@pytest.fixture
def config():
    return {"config": {"application_id": "xxx", "application_secret": "yyy", "token": "zzz", "start_date": "2021-11-01"}}


@pytest.mark.parametrize(
    ("status_code", "is_json", "response", "expected"),
    [
        (
            200,
            True,
            {
                "Token": "00000000-0000-0000-0000-000000000000",
                "Server": "https://xx-ext.linnworks.net",
                "TTL": 1234,
            },
            (True, None),
        ),
        (
            400,
            True,
            {
                "Code": None,
                "Message": "Invalid application id or application secret",
            },
            (
                False,
                "Unable to connect to Linnworks API with the provided credentials: Error while refreshing access token: Invalid application id or application secret",
            ),
        ),
        (
            400,
            False,
            "invalid_json",
            (
                False,
                "Unable to connect to Linnworks API with the provided credentials: Error while refreshing access token: 400 Client Error: None for url: https://api.linnworks.net/api/Auth/AuthorizeByApplication",
            ),
        ),
    ],
)
def test_check_connection(mocker, config, requests_mock, status_code, is_json, response, expected):
    source = SourceLinnworks()
    logger_mock = MagicMock()

    kwargs = {"status_code": status_code}
    if is_json:
        kwargs["json"] = response
    else:
        kwargs["text"] = response

    requests_mock.post("https://api.linnworks.net/api/Auth/AuthorizeByApplication", **kwargs)
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
        "TTL": 1234,
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

    with pytest.raises(Exception, match="Error while refreshing access token: Invalid application id or application secret"):
        authenticator.get_server()


def test_streams(mocker):
    source = SourceLinnworks()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
