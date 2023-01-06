#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pendulum
from source_awin.source import SourceAwin

TEST_CONFIG: dict = {
    "start_date": "2022-01-01T00:00:00Z",
    "oauth2_token": "222315a4-3620-44cc-a26e-2b7ce812fa0f" # Note: This is a randomly generated GUID.
}


def test_check_connection(mocker):
    source = SourceAwin()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    TEST_CONFIG["start_date"] = pendulum.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    source = SourceAwin()
    streams = source.streams(config=TEST_CONFIG)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
