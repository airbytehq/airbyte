#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_notion.source import SourceNotion

UNAUTHORIZED_ERROR_MESSAGE = "The provided API access token is invalid. Please double-check that you input the correct token and have granted the necessary permissions to your Notion integration."
RESTRICTED_RESOURCE_ERROR_MESSAGE = "The provided API access token does not have the correct permissions configured. Please double-check that you have granted all the necessary permissions to your Notion integration."
GENERIC_ERROR_MESSAGE = "Conflict occured while saving. Please try again."
NO_ERROR_MESSAGE = "An unexpected error occured while connecting to Notion. Please check your credentials and try again."


def test_check_connection(mocker, requests_mock):
    source = SourceNotion()
    logger_mock, config_mock = MagicMock(), {"access_token": "test_token", "start_date": "2021-01-01T00:00:00.000Z"}
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json={"results": [{"id": "aaa", "last_edited_time": "2022-01-01T00:00:00.000Z"}], "next_cursor": None},
    )
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@pytest.mark.parametrize(
    "status_code,json_response,expected_message",
    [
        (401, {"code": "unauthorized"}, UNAUTHORIZED_ERROR_MESSAGE),
        (403, {"code": "restricted_resource"}, RESTRICTED_RESOURCE_ERROR_MESSAGE),
        (409, {"message": GENERIC_ERROR_MESSAGE}, GENERIC_ERROR_MESSAGE),
        (400, {}, NO_ERROR_MESSAGE),
    ],
)
def test_check_connection_errors(mocker, requests_mock, status_code, json_response, expected_message):
    source = SourceNotion()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.post("https://api.notion.com/v1/search", status_code=status_code, json=json_response)
    result, message = source.check_connection(logger_mock, config_mock)

    assert result is False
    assert message == expected_message


def test_streams(mocker):
    source = SourceNotion()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize(
    "config, expected_token",
    [
        ({"credentials": {"auth_type": "OAuth2.0", "access_token": "oauth_token"}}, "Bearer oauth_token"),
        ({"credentials": {"auth_type": "token", "token": "other_token"}}, "Bearer other_token"),
        ({}, None),
    ],
)
def test_get_authenticator(config, expected_token):
    source = SourceNotion()
    authenticator = source._get_authenticator(config)  # Fixed line

    if expected_token:
        assert isinstance(authenticator, TokenAuthenticator)
        assert authenticator.token == expected_token  # Replace with the actual way to access the token from the authenticator
    else:
        assert authenticator is None
