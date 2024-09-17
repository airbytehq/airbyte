#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_kyve.source import SourceKyve

from . import config


def test_check_connection(mocker):
    source = SourceKyve()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceKyve()
    streams = source.streams(config)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
