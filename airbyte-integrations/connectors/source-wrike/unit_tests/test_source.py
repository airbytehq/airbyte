#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pendulum
from pytest import fixture
from source_wrike.source import SourceWrike


@fixture()
def config(request):
    args = {"access_token": "foo", "wrike_instance": "app-us2.wrike.com"}
    return args


def test_check_connection(mocker, config):
    source = SourceWrike()
    logger_mock = MagicMock()
    (connection_status, _) = source.check_connection(logger_mock, config)
    expected_status = False
    assert connection_status == expected_status


def test_streams_without_date(mocker, config):
    source = SourceWrike()
    streams = source.streams(config)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
    assert streams[-1]._start_date is not None


def test_streams_with_date(mocker, config):
    source = SourceWrike()
    streams = source.streams(config | {"start_date": "2022-05-01T00:00:00Z"})
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
    assert streams[-1]._start_date == pendulum.parse("2022-05-01T00:00:00Z")
