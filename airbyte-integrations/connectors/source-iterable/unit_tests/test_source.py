#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest
from source_iterable.api import Lists
from source_iterable.source import SourceIterable


@pytest.fixture(name="config")
def config_fixture():
    config = {"api_key": 123, "start_date": "2019-10-10T00:00:00"}
    return config


def test_source_streams():
    config = {"start_date": "2021-01-01", "api_key": "api_key"}
    streams = SourceIterable().streams(config=config)
    assert len(streams) == 44


@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_iterable.source.logger")


def test_source_check_connection_ok(config, logger_mock):
    with patch.object(Lists, "read_records", return_value=iter([1])):
        assert SourceIterable().check_connection(logger_mock, config=config) == (True, None)


def test_source_check_connection_failed(config, logger_mock):
    with patch.object(Lists, "read_records", return_value=0):
        assert SourceIterable().check_connection(logger_mock, config=config)[0] is False
