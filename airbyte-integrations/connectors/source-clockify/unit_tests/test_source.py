#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_clockify.source import SourceClockify


def setup_responses():
    responses.add(
        responses.GET,
        "https://api.clockify.me/api/v1/workspaces/workspace_id/users",
        json={"access_token": "test_api_key", "expires_in": 3600},
    )


@responses.activate
def test_check_connection(config):
    setup_responses()
    source = SourceClockify()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    source = SourceClockify()
    config_mock = MagicMock()
    streams = source.streams(config_mock)

    expected_streams_number = 7
    assert len(streams) == expected_streams_number
