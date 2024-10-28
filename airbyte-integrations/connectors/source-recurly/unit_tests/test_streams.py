#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.streams import Stream
from airbyte_protocol.models import SyncMode
from source_recurly.source import SourceRecurly


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceRecurly()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


class TestStreams:
    def test_request_params(config_pass):
        stream = get_stream_by_name("accounts", config_pass)
        expected_params = {'order': 'asc', 'sort': 'updated_at'}
        assert stream.retriever.requester.get_request_params() == expected_params

    def test_read_records(self, requests_mock, config_pass, accounts_url, mock_accounts_response):
        requests_mock.get(url=accounts_url, status_code=200, json=mock_accounts_response)
        stream = get_stream_by_name("accounts", config_pass)
        expected_parsed_records = mock_accounts_response.get("data")
        records = []
        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
        records.sort()
        expected_parsed_records.sort()
        assert len(records) == len(expected_parsed_records)
        for i in range(len(records)):
            assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())

    def test_account_coupon_redemptions_read_records(self, requests_mock, config_pass, accounts_url, mock_accounts_response, account_coupon_redemptions_url, mock_account_coupon_redemptions_response):
        requests_mock.get(url=accounts_url, status_code=200, json=mock_accounts_response)
        requests_mock.get(url=account_coupon_redemptions_url, status_code=200, json=mock_account_coupon_redemptions_response)
        stream = get_stream_by_name("account_coupon_redemptions", config_pass)
        expected_parsed_records = mock_account_coupon_redemptions_response.get("data")
        records = []
        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
        records.sort()
        expected_parsed_records.sort()
        assert len(records) == len(expected_parsed_records)
        for i in range(len(records)):
            assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())

    def test_account_notes_read_records(self, requests_mock, config_pass, accounts_url, mock_accounts_response, account_notes_url, mock_account_notes_response):
        requests_mock.get(url=accounts_url, status_code=200, json=mock_accounts_response)
        requests_mock.get(url=account_notes_url, status_code=200, json=mock_account_notes_response)
        stream = get_stream_by_name("account_notes", config_pass)
        expected_parsed_records = mock_account_notes_response.get("data")
        records = []
        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
        records.sort()
        expected_parsed_records.sort()
        assert len(records) == len(expected_parsed_records)
        for i in range(len(records)):
            assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())


    def test_coupons_read_records(self, requests_mock, config_pass, coupons_url, mock_coupons_response):
        requests_mock.get(url=coupons_url, status_code=200, json=mock_coupons_response)
        stream = get_stream_by_name("coupons", config_pass)
        expected_parsed_records = mock_coupons_response.get("data")
        records = []
        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
        records.sort()
        expected_parsed_records.sort()
        assert len(records) == len(expected_parsed_records)
        for i in range(len(records)):
            assert sorted(records[i].keys()) == sorted(expected_parsed_records[i].keys())
