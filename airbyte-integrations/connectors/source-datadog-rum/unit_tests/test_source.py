#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_datadog_rum.source import SourceDatadogRum


def test_check_connection(mocker):
    source = SourceDatadogRum()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceDatadogRum()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
