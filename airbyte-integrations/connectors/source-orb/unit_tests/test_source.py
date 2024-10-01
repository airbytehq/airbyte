#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from unittest.mock import MagicMock
from urllib import parse

from source_orb.source import SourceOrb


def get_mocked_url(base_url, config_pass):
    start_datetime = datetime.strptime(config_pass.get("start_date"), "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%dT%H:%M:%S+00:00')
    encoded_start_datetime = parse.quote(start_datetime, safe='')
    # Add an offset because the time changes by the time python makes the request
    end_datetime = (datetime.utcnow() + timedelta(milliseconds=400)).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    encoded_end_datetime = parse.quote(end_datetime, safe='')
    return base_url + "?limit=50&created_at%5Bgte%5D=" + encoded_start_datetime + "&created_at%5Blte%5D=" + encoded_end_datetime

def test_check_connection(requests_mock, config_pass, subscriptions_url, mock_subscriptions_response):
    requests_mock.get(url=get_mocked_url(subscriptions_url, config_pass), status_code=200, json=mock_subscriptions_response)
    source = SourceOrb()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config_pass) == (True, None)


def test_check_connection_fail(requests_mock, config_pass, subscriptions_url):
    print(get_mocked_url(subscriptions_url, config_pass))
    requests_mock.get(url=get_mocked_url(subscriptions_url, config_pass), status_code=401, json={"error": "Unauthorized"})
    source = SourceOrb()
    logger_mock = MagicMock()
    (status, message) = source.check_connection(logger_mock, config_pass)
    assert (status, message.split('-')[0].strip()) == (False, "Unable to connect to stream subscriptions")


def test_streams(requests_mock, config_pass, subscriptions_url, mock_subscriptions_response):
    requests_mock.get(url=get_mocked_url(subscriptions_url, config_pass), status_code=200, json=mock_subscriptions_response)
    source = SourceOrb()
    streams = source.streams(config_pass)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
