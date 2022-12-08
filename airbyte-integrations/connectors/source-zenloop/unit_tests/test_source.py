#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_zenloop.source import SourceZenloop


@responses.activate
def test_check_connection_success(mocker, config):
    responses.add(
        responses.GET,
        "https://api.zenloop.com/v1/surveys",
    )
    source = SourceZenloop()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


@responses.activate
def test_check_connection_fail(mocker, config):
    responses.add(responses.GET, "https://api.zenloop.com/v1/surveys", json={"error": "Unauthorized"}, status=401)
    source = SourceZenloop()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (
        False,
        "Unable to connect to Zenloop API with the provided credentials - 401 Client Error: Unauthorized for url: https://api.zenloop.com/v1/surveys",
    )


def test_streams(mocker):
    source = SourceZenloop()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
