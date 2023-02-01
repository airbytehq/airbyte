#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_copper.source import SourceCopper


@responses.activate
def test_check_connection(mocker):
    source = SourceCopper()
    logger_mock, config_mock = MagicMock(), MagicMock()
    url = "https://api.copper.com/developer_api/v1/people/search"
    responses.add(responses.POST, url, json={})
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceCopper()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
