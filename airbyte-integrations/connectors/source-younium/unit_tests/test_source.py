#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import responses
from source_younium.source import SourceYounium


@responses.activate
def test_check_connection(mocker):
    sandbox = False

    source = SourceYounium()
    # mock the post request

    if sandbox:
        mock_url1 = "https://younium-identity-server-sandbox.azurewebsites.net/connect/token"
        mock_url2 = "https://apisandbox.younium.com/Invoices?PageSize=1"
    else:
        mock_url1 = "https://younium-identity-server.azurewebsites.net/connect/token"
        mock_url2 = "https://api.younium.com/Invoices?PageSize=1"
    # Mock the POST to get the access token
    responses.add(
        responses.POST,
        mock_url1,
        json={
            "access_token": "dummy_token",
        },
        status=HTTPStatus.OK,
    )

    # Mock the GET to get the first page of the stream
    responses.add(responses.GET, mock_url2, json={}, status=HTTPStatus.OK)

    logger_mock = MagicMock()
    config_mock = {"playground": sandbox, "username": "dummy_username", "password": "dummy_password"}

    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceYounium()
    mocker.patch.object(source, "get_auth", return_value="dummy_token")
    config_mock = {"playground": False, "username": "dummy_username", "password": "dummy_password"}
    streams = source.streams(config_mock)

    expected_streams_number = 3
    assert len(streams) == expected_streams_number
