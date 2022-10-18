#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_insightly.source import SourceInsightly


# def test_check_connection(mocker):
#     source = SourceInsightly()
#     logger_mock, config_mock = MagicMock(), MagicMock()
#     assert source.check_connection(logger_mock, config_mock) == (True, None)


# def test_streams(mocker):
#     source = SourceInsightly()
#     config_mock = MagicMock()
#     streams = source.streams(config_mock)

#     expected_streams_number = 36
#     assert len(streams) == expected_streams_number
