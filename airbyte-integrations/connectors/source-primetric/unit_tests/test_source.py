#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_primetric.source import SourcePrimetric


def test_check_connection(mocker):
    source = SourcePrimetric()
    logger_mock, config_mock = MagicMock(), MagicMock()
    SourcePrimetric.get_connection_response = MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourcePrimetric()
    config_mock = MagicMock()
    SourcePrimetric.get_connection_response = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 21
    assert len(streams) == expected_streams_number
