#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_fortnox.source import SourceFortnox


def test_check_connection(mocker):
    source = SourceFortnox()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceFortnox()
    config_mock = {
        "credentials": {
            "access_token": "123",
            "client_id": "test",
            "client_secret": "test",
            "token_expiry_date": "1970-01-01T10:10:10Z",
            "refresh_token": "refresh_token",
        }
    }
    streams = source.streams(config_mock)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
