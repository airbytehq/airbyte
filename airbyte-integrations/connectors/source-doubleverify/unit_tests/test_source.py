#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_doubleverify.source import SourceDoubleverify
import responses


def setup_responses():
    responses.add(
        responses.GET,
        "https://data-api.doubleverify.com/requestTypes",
        json=[
            {
                "id": 1,
                "name": "Standard",
                "href": "/requestTypes/1"
            }
        ]
    )

@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceDoubleverify()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceDoubleverify()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 9
    assert len(streams) == expected_streams_number
