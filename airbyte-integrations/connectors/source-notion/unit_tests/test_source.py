#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_notion.source import SourceNotion

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


@pytest.mark.parametrize(
    "config, expected_token",
    [
        ({"credentials": {"auth_type": "OAuth2.0", "access_token": "oauth_token_123"}}, "Bearer oauth_token_123"),
        ({"credentials": {"auth_type": "token", "token": "api_token_456"}}, "Bearer api_token_456"),
        ({"access_token": "legacy_token_789"}, "Bearer legacy_token_789"),
        ({}, None),
    ],
)
def test_get_authenticator(config, expected_token):
    source = SourceNotion()
    authenticator = source._get_authenticator(config)

    if expected_token:
        assert isinstance(authenticator, TokenAuthenticator)
        assert authenticator.token == expected_token
    else:
        assert authenticator is None


def test_streams():
    source = SourceNotion()
    config_mock = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
