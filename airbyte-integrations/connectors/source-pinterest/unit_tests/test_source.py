#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_pinterest.source import SourcePinterest


def setup_responses():
    responses.add(
        responses.POST,
        "https://api.pinterest.com/v5/oauth/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
    )
    responses.add(
        responses.GET,
        "https://api.pinterest.com/v5/user_account",
        json={},
    )


@responses.activate
def test_check_connection(test_config):
    setup_responses()
    source = SourcePinterest()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


@responses.activate
def test_streams(test_config):
    setup_responses()
    source = SourcePinterest()
    streams = source.streams(test_config)
    expected_streams_number = 13
    assert len(streams) == expected_streams_number


def test_get_authenticator(test_config):
    source = SourcePinterest()
    auth = source.get_authenticator(test_config)
    expected = test_config.get("refresh_token")
    assert auth.refresh_token == expected
