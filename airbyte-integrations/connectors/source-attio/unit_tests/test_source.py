#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_attio.source import SourceAttio


def test_check_connection_ok(requests_mock):
    responses = [
        {"json": {"active": True, "scope": []}, "status_code": 200},
    ]
    source = SourceAttio()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.register_uri("GET", "https://api.attio.com/v2/self", responses)
    ok, err = source.check_connection(logger_mock, config_mock)

    assert ok
    assert not err


def test_check_connection_unauthorized(requests_mock):
    responses = [
        {"json": {"active": False}, "status_code": 200},
    ]
    source = SourceAttio()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.register_uri("GET", "https://api.attio.com/v2/self", responses)
    ok, err = source.check_connection(logger_mock, config_mock)

    assert not ok
    assert err is not None
    assert str(err) == "Connection is inactive"


def test_streams(mocker):
    source = SourceAttio()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
