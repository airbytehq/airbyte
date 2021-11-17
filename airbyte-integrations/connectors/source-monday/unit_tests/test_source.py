#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_monday.source import SourceMonday


def test_check_connection(mocker, config):
    source = SourceMonday()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_stream_count(mocker, config):
    source = SourceMonday()
    streams = source.streams(config)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
