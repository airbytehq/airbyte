#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_rki_covid.source import SourceRkiCovid


def test_check_connection(mocker):
    source = SourceRkiCovid()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceRkiCovid()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 16
    assert len(streams) == expected_streams_number
