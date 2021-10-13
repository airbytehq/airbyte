#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_onesignal.source import SourceOnesignal

def test_check_connection(mocker, requests_mock):
    source = SourceOnesignal()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://onesignal.com/api/v1/apps", json=[{
        "id": "92911750-242d-4260-9e00-9d9034f139ce",
        "name": "Your app 1",
    }])
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceOnesignal()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
