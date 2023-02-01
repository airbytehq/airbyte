#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_klarna.source import SourceKlarna


@responses.activate
def test_check_connection(mocker, source_klarna, klarna_config):
    responses.add(responses.GET, "https://api.klarna.com/settlements/v1/transactions?offset=0&size=1", json={})

    logger_mock, config_mock = MagicMock(), klarna_config
    assert source_klarna.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker, klarna_config):
    source = SourceKlarna()
    config_mock = klarna_config
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
