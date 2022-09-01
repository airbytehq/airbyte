#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses

from source_klarna.source import SourceKlarna


@responses.activate
def test_check_connection_ok(mocker):
    responses.add(responses.GET, "https://api.klarna.com/settlements/v1/transactions?offset=0&size=1", json={})

    source = SourceKlarna()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@responses.activate
def test_check_connection_failed(mocker):
    responses.add(responses.GET, "https://api.klarna.com/settlements/v1/transactions?offset=0&size=1", status=401)

    source = SourceKlarna()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (False,
                                                                 'HTTPError(\'401 Client Error: Unauthorized for url: https://api.klarna.com/settlements/v1/transactions?offset=0&size=1\')')


@responses.activate
def test_check_connection_ok_us(mocker):
    responses.add(responses.GET, "https://api-us.klarna.com/settlements/v1/transactions?offset=0&size=1", json={})

    source = SourceKlarna()
    logger_mock, config_mock = MagicMock(), {'region': 'us', 'username': '', 'password': ''}
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@responses.activate
def test_check_connection_failed_us(mocker):
    responses.add(responses.GET, "https://api-us.klarna.com/settlements/v1/transactions?offset=0&size=1", status=401)

    source = SourceKlarna()
    logger_mock, config_mock = MagicMock(), {'region': 'us', 'username': '', 'password': ''}
    assert source.check_connection(logger_mock, config_mock) == (False,
                                                                 'HTTPError(\'401 Client Error: Unauthorized for url: https://api-us.klarna.com/settlements/v1/transactions?offset=0&size=1\')')


def test_streams(mocker):
    source = SourceKlarna()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
