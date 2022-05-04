#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_kyriba.source import SourceKyriba, KyribaClient
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

config = {
    "username": "username",
    "password": "password",
    "domain": "demo.kyriba.com",
    "version": 1,
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
