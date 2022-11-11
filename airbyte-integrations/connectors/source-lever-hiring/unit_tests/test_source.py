#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_lever_hiring.source import SourceLeverHiring


def setup_responses():
    responses.add(
        responses.POST, "https://sandbox-lever.auth0.com/oauth/token", json={"access_token": "fake_access_token", "expires_in": 3600}
    )


@responses.activate
def test_check_connection(test_config):
    setup_responses()
    source = SourceLeverHiring()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


@responses.activate
def test_streams(test_config):
    setup_responses()
    source = SourceLeverHiring()
    streams = source.streams(test_config)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number
