#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import responses
from requests.exceptions import HTTPError
from source_orb.source import SourceOrb


@responses.activate
def test_check_connection_success(mocker):
    responses.add(
        responses.GET,
        "https://api.billwithorb.com/v1/ping",
    )
    source = SourceOrb()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, MagicMock()) == (True, None)


@responses.activate
def test_check_connection_fail(mocker):
    responses.add(responses.GET, "https://api.billwithorb.com/v1/ping", json={"error": "Unauthorized"}, status=401)
    source = SourceOrb()
    logger_mock = MagicMock()
    (ok, err) = source.check_connection(logger_mock, MagicMock())
    assert (ok, type(err)) == (False, HTTPError)


def test_streams(mocker):
    source = SourceOrb()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
