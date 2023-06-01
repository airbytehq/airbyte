#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_todoist.source import SourceTodoist


def test_check_connection(mocker):
    source = SourceTodoist()
    fake_info_record = {"collection": "is_mocked"}
    with patch("source_todoist.source.Tasks.read_records", MagicMock(return_value=iter([fake_info_record]))):
        logger_mock = MagicMock()
        config_mock = {"token": "test"}
        assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceTodoist()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
