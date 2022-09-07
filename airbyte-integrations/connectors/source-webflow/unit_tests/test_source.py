#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest import TestCase
from unittest.mock import MagicMock, patch

from source_webflow.source import SourceWebflow


def test_check_connection(mocker):
    source = SourceWebflow()
    fake_info_record = {"collection": "is_mocked"}
    with patch("source_webflow.source.CollectionsList.read_records", MagicMock(return_value=iter([fake_info_record]))):
        logger_mock, config_mock = MagicMock(), MagicMock()
        assert source.check_connection(logger_mock, config_mock) == (True, None)
        logger_mock.info.assert_called_once()
        my_regex = r"Successfully connected.*" + str(fake_info_record)
        TestCase().assertRegex(logger_mock.method_calls[0].args[0], my_regex)


def test_streams(mocker):
    # use the "with" to prevent the patch from impacting other tests
    with patch("source_webflow.source.SourceWebflow.generate_streams", MagicMock(return_value=["This would be a stream"])):
        source = SourceWebflow()
        config_mock = MagicMock()
        streams = source.streams(config_mock)
        assert len(streams) == 1
