#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from unittest.mock import MagicMock

import responses
from requests.exceptions import HTTPError
from source_freshservice.source import SourceFreshservice


def setup_responses():
    responses.add(
        responses.GET,
        "https://test.freshservice.com/api/v2/tickets",
        json={"per_page": 30, "order_by": "updated_at", "order_type": "asc", "updated_since": "2021-05-07T00:00:00Z"},
    )


@mock.patch("source_freshservice.streams.Tickets.read_records", return_value=iter([1]))
def test_check_connection_success(mocker):
    source = SourceFreshservice()
    logger_mock = MagicMock()
    test_config = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


def test_check_connection_failure(mocker, test_config):
    source = SourceFreshservice()
    logger_mock = MagicMock()
    response = source.check_connection(logger_mock, test_config)

    assert response[0] is False
    assert type(response[1]) == HTTPError


def test_stream_count(mocker):
    source = SourceFreshservice()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 12
    assert len(streams) == expected_streams_number
