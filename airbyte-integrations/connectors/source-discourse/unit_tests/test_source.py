#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest import TestCase
from unittest.mock import MagicMock, patch

from source_discourse.source import SourceDiscourse


def test_check_connection(mocker):
    source = SourceDiscourse()
    fake_info_record = {"posts": "are_mocked"}
    with patch("source_discourse.source.SourceDiscourse.generate_streams", MagicMock(return_value=iter([fake_info_record]))):
        logger_mock, config_mock = MagicMock(), MagicMock()
        assert source.check_connection(logger_mock, config_mock) == (True, None)
        logger_mock.info.assert_called_once()
        my_regex = r"Successfully connected.*" + str(fake_info_record)
        TestCase().assertRegex(logger_mock.method_calls[0].args[0], my_regex)

def test_streams(mocker):
    with patch("source_discourse.source.SourceDiscourse.generate_streams", MagicMock(return_value=["This would be a stream"])):
        source = SourceDiscourse()
        config_mock = MagicMock()
        streams = source.streams(config_mock)
        expected_streams_number = 3
        assert len(streams) == expected_streams_number