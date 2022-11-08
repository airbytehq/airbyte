#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_fastbill.source import SourceFastbill


@responses.activate
def test_check_connection(mocker):
    url = "https://my.fastbill.com/api/1.0/api.php"
    source = SourceFastbill()
    logger_mock, config_mock = MagicMock(), MagicMock()
    responses.add(
        responses.POST,
        url,
        json={
            "REQUEST": {
                "OFFSET": 0,
                "FILTER": [],
                "LIMIT": 0,
            },
            "RESPONSE": {
                "CUSTOMERS": "",
            },
        },
    )
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceFastbill()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
