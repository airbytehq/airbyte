#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_freshservice.source import SourceFreshservice


def test_check_connection(mocker, config):
    source = SourceFreshservice()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    source = SourceFreshservice()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 12
    assert len(streams) == expected_streams_number
