#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_confluence.source import SourceConfluence


def setup_responses():
    responses.add(
        responses.POST,
        "https://sandbox-lever.auth0.com/oauth/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
    )


def test_check_connection(mocker, config):
    setup_responses()
    source = SourceConfluence()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams_count(mocker):
    source = SourceConfluence()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
