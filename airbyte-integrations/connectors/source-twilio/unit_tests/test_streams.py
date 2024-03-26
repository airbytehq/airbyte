#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext
from unittest.mock import patch

import pendulum
import pytest
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from freezegun import freeze_time
from source_twilio.auth import HttpBasicAuthenticator
from source_twilio.source import SourceTwilio
from source_twilio.streams import (
    Accounts,
    Addresses,
    Alerts,
    Calls,
    DependentPhoneNumbers,
    MessageMedia,
    Messages,
    Recordings,
    TwilioNestedStream,
    TwilioStream,
    UsageRecords,
    UsageTriggers,
)

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

TEST_INSTANCE = SourceTwilio()


class TestTwilioStream:

    CONFIG = {"authenticator": TEST_CONFIG.get("authenticator")}

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, "accounts"),
        ],
    )
    def test_data_field(self, stream_cls, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.data_field
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, ['name']),
        ],
    )
    def test_changeable_fields(self, stream_cls, expected):
        with patch.object(Accounts, "changeable_fields", ['name']):
          stream = stream_cls(**self.CONFIG)
          result = stream.changeable_fields
          assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, "Accounts.json"),
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.path()
        assert result == expected

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
          assert result[0]['id'] == expected[0]['id']

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
        result = stream.backoff_time(response)
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
        ]
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
                {"EndTime>": "2022-01-01", "EndTime<": "2022-01-02"},
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
            result = stream.read_records(sync_mode=None)
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
                {"date_sent": "2022-11-13 23:39:00"},
                [
                    {"DateSent>": "2022-11-13 23:39:00Z", "DateSent<": "2022-11-14 23:39:00Z"},
                    {"DateSent>": "2022-11-14 23:39:00Z", "DateSent<": "2022-11-15 23:39:00Z"},
                    {"DateSent>": "2022-11-15 23:39:00Z", "DateSent<": "2022-11-16 12:03:11Z"},
                ],
            ),
            (UsageRecords, {"start_date": "2021-11-16 00:00:00"}, [{"StartDate": "2021-11-16", "EndDate": "2022-11-16"}]),
            (
                Recordings,
                {"date_created": "2021-11-16 00:00:00"},
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
        dt_ranges = list(stream.generate_date_ranges())
        assert dt_ranges == expected_dt_ranges


class TestTwilioNestedStream:

    CONFIG = {"authenticator": TEST_CONFIG.get("authenticator")}

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Addresses, {}),
            (DependentPhoneNumbers, {}),
            (MessageMedia, {"num_media": "0"}),
        ],
    )
    def test_media_exist_validation(self, stream_cls, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.media_exist_validation
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, parent_stream, record, expected",
        [
            (
                Addresses,
                Accounts,
                [{"subresource_uris": {"addresses": "123"}}],
                [{"subresource_uri": "123"}],
            ),
            (
                DependentPhoneNumbers,
                Addresses,
                [{"subresource_uris": {"addresses": "123"}, "sid": "123", "account_sid": "456"}],
                [{"sid": "123", "account_sid": "456"}],
            ),
        ],
    )
    def test_stream_slices(self, stream_cls, parent_stream, record, expected):
        stream = stream_cls(**self.CONFIG)
        with patch.object(Accounts, "read_records", return_value=record):
            with patch.object(parent_stream, "stream_slices", return_value=record):
                with patch.object(parent_stream, "read_records", return_value=record):
                    result = stream.stream_slices(sync_mode="full_refresh")
                    assert list(result) == expected


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
                [{"sid": "234", "account_sid": "678"}],
                [{"account_sid": "234"}],
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
