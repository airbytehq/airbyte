#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_it_glue.source import SourceItGlue


@fixture()
def config(request):
    args = {"api_key": "YXNmnhkjf", "fatId": "12345"}
    return args


def test_check_connection(mocker, config):
    source = SourceItGlue()
    logger_mock = MagicMock()
    (connection_status, error) = source.check_connection(logger_mock, config)
    expected_status = False
    assert connection_status == expected_status


def test_streams(mocker, config):
    source = SourceItGlue()
    streams = source.streams(config)
    expected_streams_number = 20
    assert len(streams) == expected_streams_number
