#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import pytest
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from source_twilio.auth import HttpBasicAuthenticator
from source_twilio.source import SourceTwilio
from source_twilio.streams import Accounts, Addresses, Calls, DependentPhoneNumbers, MessageMedia, Messages, UsageTriggers

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
            (Accounts, []),
        ],
    )
    def test_changeable_fields(self, stream_cls, expected):
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
            (Accounts, {"accounts": {"id": "123"}}, ["id"]),
        ],
    )
    def test_parse_response(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(**self.CONFIG)
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.parse_response(response)
        assert list(result) == expected

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


class TestIncrementalTwilioStream:

    CONFIG = TEST_CONFIG
    CONFIG.pop("account_sid")
    CONFIG.pop("auth_token")

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Calls, "EndTime>"),
        ],
    )
    def test_incremental_filter_field(self, stream_cls, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.incremental_filter_field
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, next_page_token, expected",
        [
            (
                Calls,
                {"Page": "2", "PageSize": "1000", "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95"},
                {"EndTime>": "2022-01-01", "Page": "2", "PageSize": "1000", "PageToken": "PAAD42931b949c0dedce94b2f93847fdcf95"},
            ),
        ],
    )
    def test_request_params(self, stream_cls, next_page_token, expected):
        stream = stream_cls(**self.CONFIG)
        result = stream.request_params(stream_state=None, next_page_token=next_page_token)
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
            (
                MessageMedia,
                Messages,
                [{"subresource_uris": {"media": "1234"}, "num_media": "1", "sid": "123", "account_sid": "456"}],
                [{"subresource_uri": "1234"}],
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
