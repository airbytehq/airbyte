#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

from unit_tests.conftest import get_source


def test_streams():
    config_mock = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    source = get_source(config_mock)
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


def test_streams_no_start_date_in_config():
    config_mock = {"credentials": {"auth_type": "token", "token": "abcd"}}
    source = get_source(config_mock)
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
