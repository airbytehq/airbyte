#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_glassfrog.source import SourceGlassfrog


@fixture()
def config(request):
    args = {"api_key": "xxxxxxx"}
    return args


def test_check_connection(mocker, config):
    source = SourceGlassfrog()
    logger_mock = MagicMock()
    (connection_status, error) = source.check_connection(logger_mock, config)
    expected_status = False
    assert connection_status == expected_status


def test_streams(mocker, config):
    source = SourceGlassfrog()
    streams = source.streams(config)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number
