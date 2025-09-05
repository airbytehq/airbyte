#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"

ACCOUNTS_JSON = {
    "accounts": [
        {
            "sid": "AC123",
            "date_created": "2022-01-01T00:00:00Z",
            "subresource_uris": {
                "addresses": "/2010-04-01/Accounts/AC123/Addresses.json",
                "calls": "/2010-04-01/Accounts/AC123/Calls.json",
                "messages": "/2010-04-01/Accounts/AC123/Messages.json",
                "recordings": "/2010-04-01/Accounts/AC123/Recordings.json",
            },
        }
    ],
}


def read_from_stream(cfg, stream: str, sync_mode, state=None, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(cfg, state), cfg, catalog, state, expecting_exception)


class TestTwilioStream:
    def test_next_page_token(self, requests_mock):
        accounts_page_1_json = {
            "accounts": [
                {
                    "sid": "AC123",
                    "date_created": "2022-01-01T00:00:00Z",
                    "subresource_uris": {"addresses": "/2010-04-01/Accounts/AC123/Addresses.json"},
                }
            ],
            "next_page_uri": "/2010-04-01/Accounts.json?PageSize=1000&Page=2&PageToken=PAAD42931b949c0dedce94b2f93847fdcf95",
        }
        requests_mock.get(f"{BASE}/Accounts.json", json=accounts_page_1_json, status_code=200)

        accounts_page_2_json = {
            "accounts": [
                {
                    "sid": "AC124",
                    "date_created": "2022-01-01T00:00:00Z",
                    "subresource_uris": {"addresses": "/2010-04-01/Accounts/AC123/Addresses.json"},
                }
            ]
        }
        requests_mock.get(
            f"{BASE}/Accounts.json?PageSize=1000&Page=2&PageToken=PAAD42931b949c0dedce94b2f93847fdcf95",
            json=accounts_page_2_json,
            status_code=200,
        )

        records = read_from_stream(TEST_CONFIG, "accounts", SyncMode.full_refresh).records

        assert len(records) == 2

    def test_backoff_time(self, requests_mock, mocker):
        sleep_mock = mocker.patch("time.sleep")

        requests_mock.register_uri(
            "GET",
            f"{BASE}/Accounts.json",
            [
                {"status_code": 429, "json": {}, "headers": {"retry-after": "5.5"}},
                {"status_code": 200, "json": ACCOUNTS_JSON},
            ],
        )

        records = read_from_stream(TEST_CONFIG, "accounts", SyncMode.full_refresh).records

        assert len(records) == 1
        assert sleep_mock.called
        sleep_mock.assert_any_call(pytest.approx(6.5))

    def test_transform_function(self, requests_mock):
        accounts_json = {
            "accounts": [
                {
                    "sid": "AC123",
                    "date_created": "2022-01-01T00:00:00Z",
                    "date_updated": "Fri, 11 Dec 2020 04:28:40 +0000",
                    "subresource_uris": {"addresses": "/2010-04-01/Accounts/AC123/Addresses.json"},
                }
            ]
        }
        requests_mock.get(f"{BASE}/Accounts.json", json=accounts_json, status_code=200)

        records = read_from_stream(TEST_CONFIG, "accounts", SyncMode.full_refresh).records

        assert len(records) == 1
        assert records[0].record.data["date_created"] == "2022-01-01T00:00:00Z"
        assert records[0].record.data["date_updated"] == "2020-12-11T04:28:40Z"


class TestIncrementalTwilioStream:
    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_calls_includes_date_window_params(self, requests_mock):
        requests_mock.get(f"{BASE}/Accounts.json", json=ACCOUNTS_JSON, status_code=200)

        qs = urlencode({"EndTime>": "2022-11-15", "EndTime<": "2022-11-16", "PageSize": 1000})
        requests_mock.get(
            f"{BASE}/Accounts/AC123/Calls.json?{qs}",
            json={"calls": [{"sid": "CA1", "end_time": "2022-11-15T12:00:00Z"}]},
            status_code=200,
        )

        records = read_from_stream({**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}, "calls", SyncMode.full_refresh).records
        assert len(records) == 1

    @freeze_time("2022-11-16 12:03:11+00:00")
    @pytest.mark.parametrize(
        "stream_name,path,lower_key,upper_key,state,windows",
        [
            (
                "messages",
                "/Accounts/AC123/Messages.json",
                "DateSent>",
                "DateSent<",
                {
                    "states": [
                        {
                            "partition": {"subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json"},
                            "cursor": {"date_sent": "2022-11-13T12:11:10Z"},
                        }
                    ]
                },
                [
                    ("2022-11-13 12:11:10Z", "2022-11-16 12:03:11Z"),
                ],
            ),
            (
                "usage_records",
                "/Accounts/AC123/Usage/Records/Daily.json",
                "StartDate",
                "EndDate",
                {"states": [{"partition": {"account_sid": "AC123"}, "cursor": {"start_date": "2022-11-13"}}]},
                [
                    ("2022-11-13", "2022-11-16"),
                ],
            ),
            (
                "recordings",
                "/Accounts/AC123/Recordings.json",
                "DateCreated>",
                "DateCreated<",
                {
                    "states": [
                        {
                            "partition": {"subresource_uri": "/2010-04-01/Accounts/AC123/Recordings.json"},
                            "cursor": {"date_created": "2021-11-13 00:00:00Z"},
                        }
                    ]
                },
                [
                    ("2021-11-13 00:00:00Z", "2022-11-12 23:59:59Z"),
                    ("2022-11-13 00:00:00Z", "2022-11-16 12:03:11Z"),
                ],
            ),
        ],
    )
    def test_incremental_calls_with_date_ranges(self, stream_name, path, lower_key, upper_key, state, windows, requests_mock):
        def _register_date_window(m, path, body_key, lower_key, upper_key, lower_val, upper_val):
            def _match(req):
                q = parse_qs(urlparse(req.url).query, keep_blank_values=True)
                return q.get(lower_key) == [lower_val] and q.get(upper_key) == [upper_val]

            # one matcher per window
            return m.get(f"{BASE}{path}", json={body_key: [{}]}, status_code=200, additional_matcher=_match)

        # Parent
        accounts_matcher = requests_mock.get(f"{BASE}/Accounts.json", json=ACCOUNTS_JSON, status_code=200)

        # One matcher per expected window (exact query values)
        child_matchers = [_register_date_window(requests_mock, path, stream_name, lower_key, upper_key, lo, hi) for (lo, hi) in windows]

        state = (
            StateBuilder()
            .with_stream_state(
                stream_name,
                state,
            )
            .build()
        )

        _ = read_from_stream({**TEST_CONFIG, "start_date": "2000-11-15T00:00:00Z"}, stream_name, SyncMode.incremental, state).records

        assert accounts_matcher.called, "Accounts endpoint was not called"
        assert all(m.called for m in child_matchers), "Not all date-window URLs were called"
        assert sum(m.call_count for m in child_matchers) == len(windows)


class TestTwilioNestedStream:
    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_message_media_filters_num_media_zero(self, requests_mock):
        ACCOUNTS_JSON = {
            "accounts": [
                {
                    "sid": "AC123",
                    "date_created": "2022-01-01T00:00:00Z",
                    "subresource_uris": {
                        "addresses": "/2010-04-01/Accounts/AC123/Addresses.json",
                        "calls": "/2010-04-01/Accounts/AC123/Calls.json",
                        "messages": "/2010-04-01/Accounts/AC123/Messages.json",
                        "recordings": "/2010-04-01/Accounts/AC123/Recordings.json",
                    },
                }
            ],
        }
        # Parent accounts
        requests_mock.get(f"{BASE}/Accounts.json", json=ACCOUNTS_JSON, status_code=200)

        # Messages: one with num_media "0" (should be filtered out), one with "1" (should be kept)
        messages_json = {
            "messages": [
                {
                    "sid": "SM0",
                    "account_sid": "AC123",
                    "num_media": "0",
                    "date_sent": "2022-11-16T01:00:00Z",
                    "subresource_uris": {"media": "/2010-04-01/Accounts/AC123/Messages/SM0/Media.json"},
                },
                {
                    "sid": "SM1",
                    "account_sid": "AC123",
                    "num_media": "1",
                    "date_sent": "2022-11-16T01:00:00Z",
                    "subresource_uris": {"media": "/2010-04-01/Accounts/AC123/Messages/SM1/Media.json"},
                },
            ]
        }
        # Ignore query params (date slice, PageSize, etc.) so one matcher handles all windows.
        requests_mock.get(f"{BASE}/Accounts/AC123/Messages.json", json=messages_json, status_code=200)

        # Only register the valid media endpoint (SM1). If the stream tries SM0, test will fail (unmatched request).
        media_json = {"media_list": [{"sid": "ME1", "date_created": "2022-11-16T01:05:00Z"}]}
        media_matcher = requests_mock.get(
            f"{BASE}/Accounts/AC123/Messages/SM1/Media.json",
            json=media_json,
            status_code=200,
        )

        cfg = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}
        out = read_from_stream(cfg, "message_media", SyncMode.full_refresh)
        records = out.records

        # Assert we fetched media only for SM1
        assert media_matcher.called, "Media endpoint for SM1 was not called"
        assert len(records) == 1, f"Expected 1 media record (only from SM1), got {len(records)}"

    @pytest.mark.parametrize(
        "stream_name, expected_count",
        [
            ("addresses", 1),
            ("dependent_phone_numbers", 1),
        ],
    )
    def test_stream_http_end_to_end(self, stream_name, expected_count, requests_mock):
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

        records = read_from_stream(TEST_CONFIG, stream_name, SyncMode.full_refresh).records

        assert len(records) == expected_count
