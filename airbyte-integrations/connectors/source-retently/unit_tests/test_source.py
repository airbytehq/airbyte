#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_retently.source import SourceRetently


def setup_responses():
    responses.add(
        responses.GET,
        "https://app.retently.com/api/v2/nps/customers",
        json={"data": {"subscribers": [{}]}},
    )


@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceRetently()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceRetently()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
