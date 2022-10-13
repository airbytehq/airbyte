#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_appfollow.source import SourceAppfollow


def test_check_connection(mocker, requests_mock):
    source = SourceAppfollow()
    logger_mock, config_mock = MagicMock(), MagicMock()

    # success
    requests_mock.get("https://api.appfollow.io/ratings", json={"data": "pong!"})
    assert source.check_connection(logger_mock, config_mock) == (True, None)

    # failure
    requests_mock.get("https://api.appfollow.io/ratings", status_code=500)
    ok, err = source.check_connection(logger_mock, config_mock)
    assert (ok, type(err)) == (False, str)


def test_streams(mocker):
    source = SourceAppfollow()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
