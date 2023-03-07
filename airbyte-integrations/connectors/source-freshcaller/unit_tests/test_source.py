#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
from source_freshcaller.source import FreshcallerTokenAuthenticator, SourceFreshcaller

now_dt = pendulum.now()


def test_authenticator(requests_mock):
    URL = "https://example.com/"
    TOKEN = "test_token"
    config = {
        "domain": "https://example.com",
        "api_key": "test_token",
    }
    requests_mock.post(URL, json={"token": TOKEN})
    a = FreshcallerTokenAuthenticator(config["api_key"])
    auth_headers = a.get_auth_header()
    assert auth_headers["X-Api-Auth"] == TOKEN


def test_count_streams(mocker):
    source = SourceFreshcaller()
    config_mock = mocker.MagicMock()
    streams = source.streams(config_mock)
    assert len(streams) == 4
