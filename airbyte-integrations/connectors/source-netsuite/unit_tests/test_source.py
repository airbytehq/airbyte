#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock
import requests_mock

from source_netsuite.source import SourceNetsuite

config = {
    "consumer_key": "consumer_key",
    "consumer_secret": "consumer_secret",
    "token_id": "token_id",
    "token_secret": "token_secret",
    "realm": "12345",
    "start_datetime": "2022-01-01T00:00:00Z",
}


def test_check_connection(mocker, requests_mock):
    source = SourceNetsuite()
    requests_mock.options("https://12345.suitetalk.api.netsuite.com/services/rest/*")
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_check_connection_record_types(mocker, requests_mock):
    source = SourceNetsuite()
    requests_mock.get("https://12345.suitetalk.api.netsuite.com/services/rest/record/v1/metadata-catalog/?select=currency%2Ccustomer")
    logger_mock = MagicMock()
    record_types_config = {**config, "record_types": ["currency", "customer"]}
    assert source.check_connection(logger_mock, record_types_config) == (True, None)


def test_streams(mocker):
    source = SourceNetsuite()
    source.record_types = MagicMock(return_value=["salesorder", "customer"])
    streams = source.streams(config)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
