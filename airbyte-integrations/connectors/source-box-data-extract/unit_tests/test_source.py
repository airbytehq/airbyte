#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_box_data_extract.source import SourceBoxDataExtract


def test_check_connection(mocker):
    source = SourceBoxDataExtract()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (False, "Unable to connect to Box API with the provided credentials")


def test_streams(mocker):
    source = SourceBoxDataExtract()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
