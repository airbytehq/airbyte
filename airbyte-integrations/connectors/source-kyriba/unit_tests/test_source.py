#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_kyriba.source import KyribaClient, SourceKyriba

config = {
    "username": "username",
    "password": "password",
    "domain": "demo.kyriba.com",
    "start_date": "2022-01-01",
}

config = {
    "username": "username",
    "password": "password",
    "domain": "demo.kyriba.com",
    "start_date": "2022-01-01",
}


def test_check_connection(mocker):
    source = SourceKyriba()
    KyribaClient.login = MagicMock()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    source = SourceKyriba()
    streams = source.streams(config)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
