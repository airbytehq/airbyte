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


def test_parse_date():
    # 11/10/2020 00:00:00 +3 (11/10/2020 21:00:00 GMT/UTC)
    assert ParseDates.parse_date("/Date(1602363600000+0300)/") == datetime.datetime(2020, 10, 11, 0, 0, tzinfo=datetime.timezone.utc)
    # 02/02/2020 10:31:51.5 +3 (02/02/2020 07:31:51.5 GMT/UTC)
    assert ParseDates.parse_date("/Date(1580628711500+0300)/") == datetime.datetime(2020, 2, 2, 10, 31, 51, 500000, tzinfo=datetime.timezone.utc)
    # 07/02/2022 20:12:55 GMT/UTC
    assert ParseDates.parse_date("/Date(1656792775000)/") == datetime.datetime(2022, 7, 2, 20, 12, 55, tzinfo=datetime.timezone.utc)
    # Not a date
    assert ParseDates.parse_date("not a date") is None
