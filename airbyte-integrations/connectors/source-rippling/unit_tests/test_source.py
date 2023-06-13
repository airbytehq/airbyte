#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_rippling.source import SourceRippling


@fixture()
def config(request):
    args = {"api_key": "TOKEN"}
    return args


def test_check_connection(mocker, config):
    source = SourceRippling()
    logger_mock, config_mock = MagicMock(), config
    expected_status = False
    (connection_status, _) = source.check_connection(logger_mock, config_mock)
    assert connection_status == expected_status


def test_streams(mocker):
    source = SourceRippling()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
