#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_python_http_example.source import SourcePythonHttpExample


def test_check_connection(mocker):
    source = SourcePythonHttpExample()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourcePythonHttpExample()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
