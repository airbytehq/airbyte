#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from components import TwilioConferenceParticipantsStateMigration, TwilioConferencesStateMigration
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
MONITOR_BASE = "https://monitor.twilio.com/v1"

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
                            "cursor": {"date_created": "2022-10-13 00:00:00Z"},
                        }
                    ]
                },
                [
                    ("2022-10-13 00:00:00Z", "2022-11-12 23:59:59Z"),
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

    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_messages_cursor_advances_across_windows(self, requests_mock):
        """Regression for the stuck-cursor bug (oncall #12688).

        `messages` uses a second-precision ``datetime_format`` (``%Y-%m-%d %H:%M:%SZ``). If
        ``cursor_granularity`` is finer than that (e.g. ``PT0.000001S``), each slice end
        (``next_start - granularity``) is truncated to the second when formatted, opening a
        ~1s gap between consecutive slice intervals that ``merge_intervals`` cannot bridge.
        The per-partition cursor then never advances past the first window and the stream
        re-reads its whole history every sync. With a matching granularity (``PT1S``) the
        intervals merge and the cursor advances to the newest record.

        The assertion checks the cursor lands on the *newest record across every window* (not
        merely that it moved), so a partial-advance regression where only some slices merge
        would still fail.
        """
        requests_mock.get(f"{BASE}/Accounts.json", json=ACCOUNTS_JSON, status_code=200)

        # Each monthly window returns one record dated at its lower bound (DateSent>),
        # echoed back in the ISO 'T' form the connector normalizes records to.
        windows = []

        def _messages(request, context):
            lower = parse_qs(urlparse(request.url).query, keep_blank_values=True).get("DateSent>", ["1970-01-01 00:00:00Z"])[0]
            windows.append(lower)
            context.status_code = 200
            return {"messages": [{"sid": "SM", "date_sent": lower.replace(" ", "T")}]}

        requests_mock.get(f"{BASE}/Accounts/AC123/Messages.json", json=_messages)

        # Saved per-partition state a few months back -> several monthly windows are generated.
        saved_cursor = "2022-08-16 00:00:00Z"
        state = (
            StateBuilder()
            .with_stream_state(
                "messages",
                {
                    "states": [
                        {
                            "partition": {"parent_slice": {}, "subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json"},
                            "cursor": {"date_sent": saved_cursor},
                        }
                    ],
                    "state": {"date_sent": saved_cursor},
                    "use_global_cursor": False,
                },
            )
            .build()
        )

        output = read_from_stream(TEST_CONFIG, "messages", SyncMode.incremental, state)

        # The sync must span several windows, otherwise the multi-slice merge isn't exercised.
        assert len(set(windows)) >= 3, f"expected multiple date windows, got {sorted(set(windows))}"

        # The newest record returned across all windows (records sit at each window's lower bound).
        # Window bounds and the stored cursor share the second-precision format, so a string
        # comparison is exact and order-preserving.
        newest_record = max(windows)

        # Emitted per-partition cursor must land on that newest record -- i.e. every slice merged
        # and the cursor advanced fully, not just past the first window.
        final = output.most_recent_state.stream_state.__dict__
        partition_cursor = final["states"][0]["cursor"]["date_sent"]
        assert partition_cursor == newest_record, (
            f"per-partition cursor did not advance to the newest record: "
            f"cursor={partition_cursor!r}, newest_record={newest_record!r}, saved={saved_cursor!r}"
        )

    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_alerts_pagination_limit_error_message(self, requests_mock):
        requests_mock.get(
            f"{MONITOR_BASE}/Alerts",
            json={
                "code": 400,
                "message": "Invalid page and pageSize combination, data is limited to 10,000 results",
            },
            status_code=400,
        )

        output = read_from_stream(TEST_CONFIG, "alerts", SyncMode.incremental, expecting_exception=True)

        assert not output.records
        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert "Twilio Alerts request exceeds the 10,000-result pagination limit." in output.get_formatted_error_message()
        assert "in the source configuration" in output.get_formatted_error_message()
        assert "fewer Alert records per slice" in output.get_formatted_error_message()


class TestConferenceParticipantsStream:
    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_conference_participants_only_requests_in_progress_conferences(self, requests_mock):
        accounts_json = {
            "accounts": [
                {
                    "sid": "AC123",
                    "date_created": "2022-01-01T00:00:00Z",
                    "subresource_uris": {
                        "conferences": "/2010-04-01/Accounts/AC123/Conferences.json",
                    },
                }
            ],
        }
        requests_mock.get(f"{BASE}/Accounts.json", json=accounts_json, status_code=200)

        def _match_status_in_progress(req):
            q = parse_qs(urlparse(req.url).query, keep_blank_values=True)
            return q.get("Status") == ["in-progress"]

        conferences_matcher = requests_mock.get(
            f"{BASE}/Accounts/AC123/Conferences.json",
            json={
                "conferences": [
                    {
                        "sid": "CF2",
                        "account_sid": "AC123",
                        "date_created": "2022-11-15T11:00:00Z",
                        "status": "in-progress",
                        "subresource_uris": {
                            "participants": "/2010-04-01/Accounts/AC123/Conferences/CF2/Participants.json",
                        },
                    }
                ]
            },
            status_code=200,
            additional_matcher=_match_status_in_progress,
        )

        # Participants for in-progress conference CF2
        requests_mock.get(
            f"{BASE}/Accounts/AC123/Conferences/CF2/Participants.json",
            json={
                "participants": [
                    {
                        "call_sid": "CA2",
                        "conference_sid": "CF2",
                        "account_sid": "AC123",
                        "date_created": "2022-11-15T11:01:00Z",
                        "date_updated": "2022-11-15T11:05:00Z",
                        "status": "connected",
                    }
                ]
            },
            status_code=200,
        )

        cfg = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}
        records = read_from_stream(cfg, "conference_participants", SyncMode.full_refresh).records

        assert conferences_matcher.called, "Should request conferences with Status=in-progress"
        assert len(records) == 1
        assert records[0].record.data["conference_sid"] == "CF2"

    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_conference_participants_empty_parent_returns_no_records(self, requests_mock):
        accounts_json = {
            "accounts": [
                {
                    "sid": "AC123",
                    "date_created": "2022-01-01T00:00:00Z",
                    "subresource_uris": {
                        "conferences": "/2010-04-01/Accounts/AC123/Conferences.json",
                    },
                }
            ],
        }
        requests_mock.get(f"{BASE}/Accounts.json", json=accounts_json, status_code=200)
        requests_mock.get(
            f"{BASE}/Accounts/AC123/Conferences.json",
            json={"conferences": []},
            status_code=200,
        )

        cfg = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}
        records = read_from_stream(cfg, "conference_participants", SyncMode.full_refresh).records

        assert len(records) == 0


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

    def test_services_stream_reads_from_conversations_api(self, requests_mock):
        """`services` must hit the Conversations API, not the deprecated Programmable Chat API.

        Twilio's Programmable Chat REST API (`chat.twilio.com/v2`) reaches end of life on
        June 1, 2026, so the connector routes `services` to `conversations.twilio.com/v1/Services`.
        """
        chat_matcher = requests_mock.get("https://chat.twilio.com/v2/Services", status_code=410)
        conversations_matcher = requests_mock.get(
            "https://conversations.twilio.com/v1/Services",
            json={
                "services": [
                    {
                        "sid": "IS11111111111111111111111111111111",
                        "account_sid": "AC123",
                        "friendly_name": "Default Conversations Service",
                        "date_created": "2022-01-01T00:00:00Z",
                        "date_updated": "2022-01-02T00:00:00Z",
                        "url": "https://conversations.twilio.com/v1/Services/IS11111111111111111111111111111111",
                        "links": {},
                    }
                ]
            },
            status_code=200,
        )

        records = read_from_stream(TEST_CONFIG, "services", SyncMode.full_refresh).records

        assert conversations_matcher.called, "`services` should call the Conversations API endpoint"
        assert not chat_matcher.called, "`services` must not call the deprecated Programmable Chat API endpoint"
        assert len(records) == 1

    def test_roles_stream_reads_from_conversations_api(self, requests_mock):
        """`roles` must hit the Conversations API, not the deprecated Programmable Chat API.

        The Conversations API preserves Service and Role SIDs, so existing primary keys are
        unchanged, but the request base URL must be `conversations.twilio.com/v1`.
        """
        service_sid = "IS11111111111111111111111111111111"
        requests_mock.get(
            "https://conversations.twilio.com/v1/Services",
            json={
                "services": [
                    {
                        "sid": service_sid,
                        "account_sid": "AC123",
                        "friendly_name": "Default Conversations Service",
                        "date_created": "2022-01-01T00:00:00Z",
                        "date_updated": "2022-01-02T00:00:00Z",
                        "url": f"https://conversations.twilio.com/v1/Services/{service_sid}",
                        "links": {},
                    }
                ]
            },
            status_code=200,
        )
        chat_roles_matcher = requests_mock.get(f"https://chat.twilio.com/v2/Services/{service_sid}/Roles", status_code=410)
        conversations_roles_matcher = requests_mock.get(
            f"https://conversations.twilio.com/v1/Services/{service_sid}/Roles",
            json={
                "roles": [
                    {
                        "sid": "RL22222222222222222222222222222222",
                        "account_sid": "AC123",
                        "chat_service_sid": service_sid,
                        "friendly_name": "service admin",
                        "type": "service",
                        "permissions": ["editAnyMessage"],
                        "date_created": "2022-01-01T00:00:00Z",
                        "date_updated": "2022-01-02T00:00:00Z",
                        "url": f"https://conversations.twilio.com/v1/Services/{service_sid}/Roles/RL22222222222222222222222222222222",
                    }
                ]
            },
            status_code=200,
        )

        records = read_from_stream(TEST_CONFIG, "roles", SyncMode.full_refresh).records

        assert conversations_roles_matcher.called, "`roles` should call the Conversations API endpoint"
        assert not chat_roles_matcher.called, "`roles` must not call the deprecated Programmable Chat API endpoint"
        assert len(records) == 1
        assert records[0].record.data["chat_service_sid"] == service_sid

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


@pytest.mark.parametrize(
    "input_state,expected_state,should_migrate",
    [
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    }
                ]
            },
            {
                "states": [
                    {
                        "partition": {
                            "conference_status": "completed",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "conference_status": "in-progress",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            True,
            id="single_partition_duplicated_for_both_statuses",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-10-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "subresource_uri": "/2010-04-01/Accounts/AC456/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            {
                "states": [
                    {
                        "partition": {
                            "conference_status": "completed",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-10-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "conference_status": "in-progress",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-10-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "conference_status": "completed",
                            "subresource_uri": "/2010-04-01/Accounts/AC456/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "conference_status": "in-progress",
                            "subresource_uri": "/2010-04-01/Accounts/AC456/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            True,
            id="multiple_partitions_each_duplicated_with_own_cursor",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                    }
                ]
            },
            {
                "states": [
                    {
                        "partition": {
                            "conference_status": "completed",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {},
                    },
                    {
                        "partition": {
                            "conference_status": "in-progress",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {},
                    },
                ]
            },
            True,
            id="partition_without_cursor_gets_empty_cursor",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "conference_status": "completed",
                            "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                            "parent_slice": {},
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            None,
            False,
            id="already_migrated_no_op",
        ),
        pytest.param(
            {},
            None,
            False,
            id="empty_state_no_op",
        ),
    ],
)
def test_conferences_state_migration(input_state, expected_state, should_migrate):
    migration = TwilioConferencesStateMigration()
    assert migration.should_migrate(input_state) == should_migrate
    if should_migrate:
        assert migration.migrate(input_state) == expected_state


@pytest.mark.parametrize(
    "input_state,expected_state,should_migrate",
    [
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    }
                ]
            },
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "conference_status": "in-progress",
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            True,
            id="single_partition_adds_conference_status_to_parent_slice",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-10-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC456/Conferences/CF2/Participants.json"},
                            "parent_slice": {
                                "subresource_uri": "/2010-04-01/Accounts/AC456/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "conference_status": "in-progress",
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-10-01T00:00:00Z"},
                    },
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC456/Conferences/CF2/Participants.json"},
                            "parent_slice": {
                                "conference_status": "in-progress",
                                "subresource_uri": "/2010-04-01/Accounts/AC456/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            True,
            id="multiple_partitions_each_duplicated_with_own_cursor",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                    }
                ]
            },
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "conference_status": "in-progress",
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {},
                    },
                ]
            },
            True,
            id="partition_without_cursor_gets_empty_cursor",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "conference_status": "completed",
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            {"states": []},
            True,
            id="completed_partitions_are_removed",
        ),
        pytest.param(
            {
                "states": [
                    {
                        "partition": {
                            "subresource_uris": {"participants": "/2010-04-01/Accounts/AC123/Conferences/CF1/Participants.json"},
                            "parent_slice": {
                                "conference_status": "in-progress",
                                "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
                                "parent_slice": {},
                            },
                        },
                        "cursor": {"date_created": "2022-11-01T00:00:00Z"},
                    },
                ]
            },
            None,
            False,
            id="already_migrated_no_op",
        ),
        pytest.param(
            {},
            None,
            False,
            id="empty_state_no_op",
        ),
    ],
)
def test_conference_participants_state_migration(input_state, expected_state, should_migrate):
    migration = TwilioConferenceParticipantsStateMigration()
    assert migration.should_migrate(input_state) == should_migrate
    if should_migrate:
        assert migration.migrate(input_state) == expected_state
