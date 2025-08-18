#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext
from unittest.mock import patch

import pendulum
import pytest
import requests
from freezegun import freeze_time
from source_twilio.auth import HttpBasicAuthenticator
from source_twilio.source import SourceTwilio
from source_twilio.streams import (
    Accounts,
    Alerts,
    Calls,
    MessageMedia,
    Messages,
    Recordings,
    TwilioNestedStream,
    TwilioStream,
    UsageRecords,
    UsageTriggers,
)

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http import HttpStream


TEST_CONFIG = {
    "account_sid": "airbyte.io",
    "auth_token": "secret",
    "start_date": "2022-01-01T00:00:00Z",
    "lookback_window": 0,
}
TEST_CONFIG.update(
    **{
        "authenticator": HttpBasicAuthenticator((TEST_CONFIG["account_sid"], TEST_CONFIG["auth_token"])),
    }
)

TEST_INSTANCE = SourceTwilio(TEST_CONFIG, None, None)


def find_stream(stream_name, config, state=None):
    streams = SourceTwilio(config, None, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def read_full_refresh(stream_instance):
    res = []
    schema = stream_instance.get_json_schema()
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records = stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            stream_instance.transformer.transform(record, schema)
            res.append(record)
    return res


class TestTwilioStream:
    CONFIG = {"authenticator": TEST_CONFIG.get("authenticator")}

    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (
                Accounts,
                {
                    "next_page_uri": "/2010-04-01/Accounts/ACdad/Addresses.json?PageSize=1000&Page=2&PageToken=PAAD42931b949c0dedce94b2f93847fdcf95"
                },
                {"Page": "2", "PageSize": "1000", "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95"},
            ),
        ],
    )
    def test_next_page_token(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(**self.CONFIG)
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.next_page_token(response)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (Accounts, {"accounts": [{"id": "123", "name": "test"}]}, [{"id": "123"}]),
        ],
    )
    def test_parse_response(self, requests_mock, stream_cls, test_response, expected):
        with patch.object(TwilioStream, "changeable_fields", ["name"]):
            stream = stream_cls(**self.CONFIG)
            url = f"{stream.url_base}{stream.path()}"
            requests_mock.get(url, json=test_response)
            response = requests.get(url)
            result = list(stream.parse_response(response))
            assert result[0]["id"] == expected[0]["id"]

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, "5.5"),
        ],
    )
    def test_backoff_time(self, requests_mock, stream_cls, expected):
        stream = stream_cls(**self.CONFIG)
        url = f"{stream.url_base}{stream.path()}"
        test_headers = {"Retry-After": expected}
        requests_mock.get(url, headers=test_headers)
        response = requests.get(url)
        response.status_code = 429
        result = stream.get_backoff_strategy().backoff_time(response, 1)
        assert result == float(expected)

    @pytest.mark.parametrize(
        "stream_cls, next_page_token, expected",
        [
            (
                Accounts,
                {"Page": "2", "PageSize": "1000", "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95"},
                {"Page": "2", "PageSize": "1000", "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95"},
            ),
        ],
    )
    def test_request_params(self, stream_cls, next_page_token, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.request_params(stream_state=None, next_page_token=next_page_token)
        assert result == expected

    @pytest.mark.parametrize(
        "original_value, field_schema, expected_value",
        [
            ("Fri, 11 Dec 2020 04:28:40 +0000", {"format": "date-time"}, "2020-12-11T04:28:40Z"),
            ("2020-12-11T04:28:40Z", {"format": "date-time"}, "2020-12-11T04:28:40Z"),
            ("some_string", {}, "some_string"),
        ],
    )
    def test_transform_function(self, original_value, field_schema, expected_value):
        assert Accounts.custom_transform_function(original_value, field_schema) == expected_value


class TestIncrementalTwilioStream:
    CONFIG = TEST_CONFIG
    CONFIG.pop("account_sid")
    CONFIG.pop("auth_token")

    @pytest.mark.parametrize(
        "stream_cls, stream_slice, next_page_token, expected",
        [
            (
                Calls,
                StreamSlice(partition={}, cursor_slice={"EndTime>": "2022-01-01", "EndTime<": "2022-01-02"}),
                {"Page": "2", "PageSize": "1000", "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95"},
                {
                    "EndTime>": "2022-01-01",
                    "EndTime<": "2022-01-02",
                    "Page": "2",
                    "PageSize": "1000",
                    "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95",
                },
            ),
        ],
    )
    def test_request_params(self, stream_cls, stream_slice, next_page_token, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.request_params(stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, record, expected",
        [
            (Calls, [{"end_time": "2022-02-01T00:00:00Z"}], [{"end_time": "2022-02-01T00:00:00Z"}]),
        ],
    )
    def test_read_records(self, stream_cls, record, expected):
        stream = stream_cls(**self.CONFIG)
        with patch.object(HttpStream, "read_records", return_value=record):
            result = stream.read_records(sync_mode=None, stream_slice=StreamSlice(partition={}, cursor_slice={}))
            assert list(result) == expected

    @pytest.mark.parametrize(
        "stream_cls, parent_cls_records, extra_slice_keywords",
        [
            (Calls, [{"subresource_uris": {"calls": "123"}}, {"subresource_uris": {"calls": "124"}}], ["subresource_uri"]),
            (Alerts, [{}], []),
        ],
    )
    def test_stream_slices(self, mocker, stream_cls, parent_cls_records, extra_slice_keywords):
        stream = stream_cls(
            authenticator=TEST_CONFIG.get("authenticator"), start_date=pendulum.now().subtract(months=13).to_iso8601_string()
        )
        expected_slices = 2 * len(parent_cls_records)  # 2 per year slices per each parent slice
        if isinstance(stream, TwilioNestedStream):
            slices_mock_context = mocker.patch.object(stream.parent_stream_instance, "stream_slices", return_value=[{}])
            records_mock_context = mocker.patch.object(stream.parent_stream_instance, "read_records", return_value=parent_cls_records)
        else:
            slices_mock_context, records_mock_context = nullcontext(), nullcontext()
        with slices_mock_context:
            with records_mock_context:
                slices = list(stream.stream_slices(sync_mode="incremental"))
        assert len(slices) == expected_slices
        for slice_ in slices:
            if isinstance(stream, TwilioNestedStream):
                for kw in extra_slice_keywords:
                    assert kw in slice_
            assert slice_[stream.lower_boundary_filter_field] <= slice_[stream.upper_boundary_filter_field]

    @freeze_time("2022-11-16 12:03:11+00:00")
    @pytest.mark.parametrize(
        "stream_cls, state, expected_dt_ranges",
        (
            (
                Messages,
                {
                    "states": [
                        {
                            "partition": {"key": "value"},
                            "cursor": {"date_sent": "2022-11-13 23:39:00"},
                        }
                    ]
                },
                [
                    {"DateSent>": "2022-11-13 23:39:00Z", "DateSent<": "2022-11-14 23:39:00Z"},
                    {"DateSent>": "2022-11-14 23:39:00Z", "DateSent<": "2022-11-15 23:39:00Z"},
                    {"DateSent>": "2022-11-15 23:39:00Z", "DateSent<": "2022-11-16 12:03:11Z"},
                ],
            ),
            (
                UsageRecords,
                {
                    "states": [
                        {
                            "partition": {"key": "value"},
                            "cursor": {"start_date": "2021-11-16 00:00:00"},
                        }
                    ]
                },
                [{"StartDate": "2021-11-16", "EndDate": "2022-11-16"}],
            ),
            (
                Recordings,
                {
                    "states": [
                        {
                            "partition": {"key": "value"},
                            "cursor": {"date_created": "2021-11-16 00:00:00"},
                        }
                    ]
                },
                [
                    {"DateCreated>": "2021-11-16 00:00:00Z", "DateCreated<": "2022-11-16 00:00:00Z"},
                    {"DateCreated>": "2022-11-16 00:00:00Z", "DateCreated<": "2022-11-16 12:03:11Z"},
                ],
            ),
        ),
    )
    def test_generate_dt_ranges(self, stream_cls, state, expected_dt_ranges):
        stream = stream_cls(authenticator=TEST_CONFIG.get("authenticator"), start_date="2000-01-01 00:00:00")
        stream.state = state
        dt_ranges = list(stream.generate_date_ranges({"key": "value"}))
        assert dt_ranges == expected_dt_ranges


class TestTwilioNestedStream:
    CONFIG = {"account_sid": "AC_TEST", "auth_token": "secret", "start_date": "2022-01-01T00:00:00Z"}

    # Add this test when message media is migrated to low code
    # @pytest.mark.parametrize(
    #     "stream_cls, expected",
    #     [
    #         (Addresses, {}),
    #         (DependentPhoneNumbers, {}),
    #         (MessageMedia, {"num_media": "0"})
    #     ],
    # )
    # def test_media_exist_validation(self, stream_cls, expected):
    #     stream = stream_cls(**self.CONFIG)
    #     result = stream.media_exist_validation
    #     assert result == expected

    @pytest.mark.parametrize(
        "stream_name, expected_count",
        [
            ("addresses", 1),
            ("dependent_phone_numbers", 1),
        ],
    )
    def test_stream_http_end_to_end(self, stream_name, expected_count, requests_mock):
        BASE = "https://api.twilio.com/2010-04-01"

        # 1) Parent: Accounts (provides the subresource_uris.addresses link)
        accounts_json = {
            "accounts": [
                {
                    "sid": "AC123",
                    "date_created": "2022-01-01T00:00:00Z",
                    "subresource_uris": {"addresses": "/2010-04-01/Accounts/AC123/Addresses.json"},
                }
            ]
        }
        requests_mock.get(f"{BASE}/Accounts.json", json=accounts_json, status_code=200)

        # 2) Child: Addresses (collection key must match the stream name: "addresses")
        addresses_json = {"addresses": [{"sid": "AD1", "account_sid": "AC123"}]}
        requests_mock.get(f"{BASE}/Accounts/AC123/Addresses.json", json=addresses_json, status_code=200)

        # 3) Grandchild: DependentPhoneNumbers (collection key must be "dependent_phone_numbers")
        if stream_name == "dependent_phone_numbers":
            dpn_json = {"dependent_phone_numbers": [{"sid": "PN1", "account_sid": "AC123"}]}
            requests_mock.get(
                f"{BASE}/Accounts/AC123/Addresses/AD1/DependentPhoneNumbers.json",
                json=dpn_json,
                status_code=200,
            )

        # find the stream from the low-code source and read
        stream = find_stream(stream_name, self.CONFIG)
        records = read_full_refresh(stream)

        assert len(records) == expected_count


class TestUsageNestedStream:
    CONFIG = {"authenticator": TEST_CONFIG.get("authenticator")}

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (UsageTriggers, "Triggers"),
        ],
    )
    def test_path_name(self, stream_cls, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.path_name
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, parent_stream, record, expected",
        [
            (
                UsageTriggers,
                Accounts,
                [{"sid": "234", "account_sid": "678", "date_created": "2022-11-16 00:00:00"}],
                [StreamSlice(partition={"account_sid": "234", "date_created": "2022-11-16 00:00:00"}, cursor_slice={})],
            ),
        ],
    )
    def test_stream_slices(self, stream_cls, parent_stream, record, expected):
        stream = stream_cls(**self.CONFIG)
        with patch.object(Accounts, "read_records", return_value=record):
            with patch.object(parent_stream, "stream_slices", return_value=record):
                with patch.object(parent_stream, "read_records", return_value=record):
                    result = stream.stream_slices()
                    assert list(result) == expected
