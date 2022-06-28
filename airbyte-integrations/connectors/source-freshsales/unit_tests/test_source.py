#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_freshsales.source import SourceFreshsales

# Test `test_check_connection` has been commented out, due to innactive test account.
# TODO: please uncomment this test, once the integration test account works again.

# def test_check_connection(mocker, config):
#     source = SourceFreshsales()
#     logger_mock = MagicMock()
#     assert source.check_connection(logger_mock, config) == (True, None)


def test_count_streams(mocker):
    source = SourceFreshsales()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 9
    assert len(streams) == expected_streams_number
