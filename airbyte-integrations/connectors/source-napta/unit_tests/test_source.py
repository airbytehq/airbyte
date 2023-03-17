#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_napta.source import SourceNapta


def test_check_connection(mocker):
    source = SourceNapta()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceNapta()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 70
    assert len(streams) == expected_streams_number
