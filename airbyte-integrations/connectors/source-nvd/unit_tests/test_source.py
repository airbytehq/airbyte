#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_nvd.source import SourceNvd


def test_check_connection(mocker):
    source = SourceNvd()
    logger_mock, config_mock = MagicMock(), {"modStartDate": "2022-01-01T00:00:00"}
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceNvd()
    config_mock = {"modStartDate": "2022-01-01T00:00:00"}
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
