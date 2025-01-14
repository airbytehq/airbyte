#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_gridly.source import SourceGridly


CONFIG = {"api_key": "IbuIBdkFjrJps6", "grid_id": "4539o52kmdjmzwp"}


def test_check_connection(mocker):
    source = SourceGridly()
    logger_mock, config_mock = MagicMock(), CONFIG
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceGridly()
    config_mock = CONFIG
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
