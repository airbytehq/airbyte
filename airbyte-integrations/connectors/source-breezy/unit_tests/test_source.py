#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_breezy.source import SourceBreezy


def test_check_connection(mocker):
    source = SourceBreezy()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceBreezy()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
