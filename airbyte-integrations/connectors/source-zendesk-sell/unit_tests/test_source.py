#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_zendesk_sell.source import SourceZendeskSell


def test_check_connection(mocker):
    source = SourceZendeskSell()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceZendeskSell()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 23
    assert len(streams) == expected_streams_number
