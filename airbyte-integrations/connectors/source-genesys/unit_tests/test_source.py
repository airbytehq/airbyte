#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_genesys.source import SourceGenesys


def test_check_connection(mocker):
    source = SourceGenesys()
    logger_mock, config_mock = MagicMock(), MagicMock()
    SourceGenesys.get_connection_response = MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceGenesys()
    config_mock = MagicMock()
    SourceGenesys.get_connection_response = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 16
    assert len(streams) == expected_streams_number
