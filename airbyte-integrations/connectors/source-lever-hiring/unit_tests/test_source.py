#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from conftest import test_config
from source_lever_hiring.source import SourceLeverHiring


@pytest.mark.parametrize(
    ("response", "url", "payload", "test_config"),
    [
        (
            responses.POST,
            "https://sandbox-lever.auth0.com/oauth/token",
            {"access_token": "fake_access_token", "expires_in": 3600},
            test_config(auth_type="Client"),
        )(
            responses.GET,
            "https://api.lever.co/v1/opportunities",
            {"api_key": "fake_api_key", "expires_in": 3600},
            test_config(auth_type="Api Key"),
        ),
    ],
)
@responses.activate
def test_check_connection(response, url, payload, test_config):
    responses.add(response, url, payload)
    source = SourceLeverHiring()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


@responses.activate
def test_streams(response, url, payload, test_config):
    responses.add(response, url, payload)
    source = SourceLeverHiring()
    streams = source.streams(test_config)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number
