#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, ANY

import requests
from source_paystack.source import SourcePaystack


def test_check_connection_success(mocker, requests_mock):
    source = SourcePaystack()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://api.paystack.co/customer", json={ "status": True })

    assert source.check_connection(logger_mock, config_mock) == (True, None)

def test_check_connection_failure(mocker, requests_mock):
    source = SourcePaystack()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://api.paystack.co/customer", json={ "status": False, "message": "Failed" })

    assert source.check_connection(logger_mock, config_mock) == (False, ANY)

def test_check_connection_error(mocker, requests_mock):
    source = SourcePaystack()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://api.paystack.co/customer", exc=requests.exceptions.ConnectTimeout)

    assert source.check_connection(logger_mock, config_mock) == (False, ANY)

def test_streams(mocker):
    source = SourcePaystack()
    streams = source.streams({"start_date": "2020-08-01", "secret_key": "sk_test_123456"})

    assert len(streams) == 1
