#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_zenefits.source import SourceZenefits


@fixture()
def config(request):
    args = {"token": "YXNmnhkjf"}
    return args


def test_check_connection(mocker, config):
    source = SourceZenefits()
    logger_mock = MagicMock()
    (connection_status, error) = source.check_connection(logger_mock, config)
    expected_status = False
    assert connection_status == expected_status


def test_streams(mocker, config):
    source = SourceZenefits()
    streams = source.streams(config)
    expected_streams_number = 11
    assert len(streams) == expected_streams_number
