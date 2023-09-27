#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import freezegun
import pytest
from source_notion.source import SourceNotion

UNAUTHORIZED_ERROR_MESSAGE = "The provided API access token is invalid. Please double-check that you input the correct token and have granted the necessary permissions to your Notion integration."
RESTRICTED_RESOURCE_ERROR_MESSAGE = "The provided API access token does not have the correct permissions configured. Please double-check that you have granted all the necessary permissions to your Notion integration."
GENERIC_ERROR_MESSAGE = "Conflict occured while saving. Please try again."
NO_ERROR_MESSAGE = "An unexpected error occured while connecting to Notion. Please check your credentials and try again."


def test_check_connection(mocker, requests_mock):
    source = SourceNotion()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.post("https://api.notion.com/v1/search", json={"results": [{"id": "aaa"}], "next_cursor": None})
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@pytest.mark.parametrize(
        "status_code,json_response,expected_message",
        [
            (401, {"code": "unauthorized"}, UNAUTHORIZED_ERROR_MESSAGE),
            (403, {"code": "restricted_resource"}, RESTRICTED_RESOURCE_ERROR_MESSAGE),
            (409, {"message": GENERIC_ERROR_MESSAGE}, GENERIC_ERROR_MESSAGE),
            (400, {}, NO_ERROR_MESSAGE)
        ]
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
    expected_streams_number = 4
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize("config, expected_start_date", [
    ({"start_date": "2021-09-01T00:00:00.000Z", "authenticator": "super_secret_token"}, "2021-09-01T00:00:00.000Z"),
    ({"authenticator": "even_more_secret_token"}, '2020-09-22T00:00:00.000Z'),
    ({"authenticator": "even_more_secret_token", "start_date": None}, '2020-09-22T00:00:00.000Z'),
])
@freezegun.freeze_time("2022-09-22T00:00:00.000Z")
def test_set_start_date(config, expected_start_date):
    """
    Test that start_date in config is either:
      1. set to the value provided by the user
      2. defaults to two years from the present date set by the test environment.
    """
    SourceNotion.set_start_date(config)
    assert config["start_date"] == expected_start_date
