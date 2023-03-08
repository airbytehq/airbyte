#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_tenkft.source import SourceTenkft


def test_check_connection_ok(config, mock_stream, mock_responses):
    logger_mock = MagicMock()
    mock_stream("users", response=mock_responses.get("Users"))
    assert SourceTenkft().check_connection(logger_mock, config=config) == (True, None)


def test_streams(mocker):
    source = SourceTenkft()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
