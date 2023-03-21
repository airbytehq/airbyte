#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_confluence.source import SourceConfluence


def setup_responses():
    responses.add(
        responses.GET,
        "https://example.atlassian.net/wiki/rest/api/space",
        json={"access_token": "test_api_key", "expires_in": 3600},
    )


@responses.activate
def test_check_connection(config):
    setup_responses()
    source = SourceConfluence()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_check_connection_failed(config):
    source = SourceConfluence()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config)[0] is False


@responses.activate
def test_streams_count(config):
    responses.add(
        responses.GET,
        "https://example.atlassian.net/wiki/rest/api/audit",
        status=200,
    )
    source = SourceConfluence()
    streams = source.streams(config)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
