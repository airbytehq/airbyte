#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_lemlist.source import SourceLemlist


@patch("source_lemlist.source.Team.read_records", return_value=iter(["item"]))
def test_check_connection(_):
    test_config = {"api_key": "test-api-key"}
    logger_mock = MagicMock()

    source = SourceLemlist()
    valid_connection, error = source.check_connection(logger_mock, test_config)

    assert valid_connection


def test_streams():
    source = SourceLemlist()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
