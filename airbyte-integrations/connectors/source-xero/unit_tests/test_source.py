#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

from source_xero.source import SourceXero


def test_check_connection(requests_mock, config_pass, mock_bank_transaction_response):
    requests_mock.get(url="https://api.xero.com/api.xro/2.0/BankTransactions", status_code=200, json=mock_bank_transaction_response)
    source = SourceXero()
    status, msg = source.check_connection(logging.getLogger(), config_pass)
    assert (status, msg) == (True, None)


def test_check_connection_failed(bad_config, requests_mock):
    requests_mock.get(url="https://api.xero.com/api.xro/2.0/BankTransactions", status_code=400, json=[])
    source = SourceXero()
    check_succeeded, error = source.check_connection(MagicMock(), bad_config)
    assert check_succeeded is False
    assert error == "" or "none" in error.lower()


def test_streams_count(config_pass):
    source = SourceXero()
    streams = source.streams(config_pass)
    expected_streams_number = 21
    assert len(streams) == expected_streams_number
