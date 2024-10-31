#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.models import SyncMode
from conftest import get_stream_by_name
from source_xero.components import ParseDates


def test_parsed_result(requests_mock, config_pass, mock_bank_transaction_response):
    requests_mock.get(url="https://api.xero.com/api.xro/2.0/BankTransactions", status_code=200, json=mock_bank_transaction_response["BankTransactions"])
    stream = get_stream_by_name("bank_transactions", config_pass)
    expected_record = mock_bank_transaction_response["BankTransactions"]
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


def test_request_params(config_pass):
    bank_transactions = get_stream_by_name("bank_transactions", config_pass)
    expected_params = {}
    assert bank_transactions.retriever.requester.get_request_params() == expected_params


def test_request_headers(config_pass):
    bank_transactions = get_stream_by_name("bank_transactions", config_pass)
    expected_headers = {'Xero-Tenant-Id': 'goodone', 'Accept': 'application/json'}
    assert bank_transactions.retriever.requester.get_request_headers() == expected_headers 


def test_http_method(config_pass):
    stream = get_stream_by_name("bank_transactions", config_pass)
    expected_method = "GET"
    actual_method = stream.retriever.requester.http_method.value
    assert actual_method == expected_method


def test_ignore_forbidden(requests_mock, config_pass):
    requests_mock.get(url="https://api.xero.com/api.xro/2.0/BankTransactions", status_code=403, json=[{ "message": "Forbidden resource"}])
    stream = get_stream_by_name("bank_transactions", config_pass)

    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert records == []
    assert requests_mock.call_count == 1


def test_parse_date():
    # 11/10/2020 00:00:00 +3 (11/10/2020 21:00:00 GMT/UTC)
    assert ParseDates.parse_date("/Date(1602363600000+0300)/") == datetime.datetime(2020, 10, 11, 0, 0, tzinfo=datetime.timezone.utc)
    # 02/02/2020 10:31:51.5 +3 (02/02/2020 07:31:51.5 GMT/UTC)
    assert ParseDates.parse_date("/Date(1580628711500+0300)/") == datetime.datetime(2020, 2, 2, 10, 31, 51, 500000, tzinfo=datetime.timezone.utc)
    # 07/02/2022 20:12:55 GMT/UTC
    assert ParseDates.parse_date("/Date(1656792775000)/") == datetime.datetime(2022, 7, 2, 20, 12, 55, tzinfo=datetime.timezone.utc)
    # Not a date
    assert ParseDates.parse_date("not a date") is None
