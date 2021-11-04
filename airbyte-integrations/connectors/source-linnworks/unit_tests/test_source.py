#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_linnworks.source import SourceLinnworks


@fixture
def config():
    return {
        "config": {
            "application_id": "xxx",
            "application_secret": "yyy",
            "token": "zzz",
            "start_date": "2021-11-01"
        }
    }


def test_check_connection(mocker, requests_mock, config):
    source = SourceLinnworks()
    logger_mock = MagicMock()
    requests_mock.post(
        "https://api.linnworks.net/api/Auth/AuthorizeByApplication",
        json={
            "Token": "00000000-0000-0000-0000-000000000000",
            "Server": "https://xx-ext.linnworks.net",
        },
    )
    assert source.check_connection(logger_mock, **config) == (True, None)

def test_streams(mocker):
    source = SourceLinnworks()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
