#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_vtex.source import SourceVtex


def test_check_connection(mocker):
    source = SourceVtex()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock)[0] == False


def test_streams(mocker):
    source = SourceVtex()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
