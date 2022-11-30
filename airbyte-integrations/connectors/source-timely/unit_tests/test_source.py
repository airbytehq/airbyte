#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_timely.source import SourceTimely


@fixture()
def config(request):
    args = {"account_id": "123", "start_date": "2022-04-01", "bearer_token": "51UWRAsFuIbeygfIY3XfucQUGiX"}
    return args


def test_check_connection(mocker, config):
    source = SourceTimely()
    logger_mock = MagicMock()
    (connection_status, error) = source.check_connection(logger_mock, config)
    expected_status = False
    assert connection_status == expected_status


def test_streams(mocker, config):
    source = SourceTimely()
    streams = source.streams(config)
    # TODO: replace this with your streams number
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
