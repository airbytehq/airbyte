#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_onesignal.source import SourceOnesignal


@fixture
def config():
    return {"config": {"user_auth_key": "", "start_date": "2021-01-01T00:00:00Z", "outcome_names": ""}}


def test_check_connection(mocker, requests_mock, config):
    source = SourceOnesignal()
    logger_mock = MagicMock()
    requests_mock.get(
        "https://onesignal.com/api/v1/apps",
        json=[
            {
                "id": "92911750-242d-4260-9e00-9d9034f139ce",
                "basic_auth_key": "your key",
            }
        ],
    )
    assert source.check_connection(logger_mock, **config) == (True, None)


def test_streams(mocker, config):
    source = SourceOnesignal()
    streams = source.streams(**config)
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
