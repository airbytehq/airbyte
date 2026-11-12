# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize(
    "stream,resource,body_key,cursor,lower_key,upper_key,datetime_format",
    [
        ("messages", "Messages", "messages", "date_sent", "DateSent>", "DateSent<", "%Y-%m-%d %H:%M:%SZ"),
        ("recordings", "Recordings", "recordings", "date_created", "DateCreated>", "DateCreated<", "%Y-%m-%d %H:%M:%SZ"),
        ("calls", "Calls", "calls", "end_time", "EndTime>", "EndTime<", "%Y-%m-%d"),
        ("conferences", "Conferences", "conferences", "date_created", "DateCreated>", "DateCreated<", "%Y-%m-%d"),
        ("usage_records", "Usage/Records/Daily", "usage_records", "start_date", "StartDate", "EndDate", "%Y-%m-%d"),
        ("message_media", "Messages/SM123/Media", "media_list", "date_created", "DateCreated>", "DateCreated<", "%Y-%m-%d"),
    ],
)
@pytest.mark.parametrize("legacy_partition", [False, True])
def test_global_cursor_ignores_stale_partitions(
    requests_mock, legacy_partition, stream, resource, body_key, cursor, lower_key, upper_key, datetime_format
):
    global_cursor = "2022-11-15T12:00:00Z"
    partitions = []
    requests = []
    accounts = []
    for account in ("AC123", "AC456"):
        uri = f"/2010-04-01/Accounts/{account}/{resource}.json"
        partition = {"account_sid": account} if stream == "usage_records" else {"subresource_uri": uri}
        if not legacy_partition:
            partition["parent_slice"] = {}
            if stream == "message_media":
                partition["parent_slice"] = {
                    "subresource_uri": f"/2010-04-01/Accounts/{account}/Messages.json",
                    "parent_slice": {},
                }
            if stream == "conferences":
                partition["conference_status"] = "completed"
        partitions.append({"partition": partition, "cursor": {cursor: "2022-11-14T00:00:00Z"}})
        if stream == "message_media":
            messages_uri = f"/2010-04-01/Accounts/{account}/Messages.json"
            requests_mock.get(
                f"https://api.twilio.com{messages_uri}",
                json={
                    "messages": [
                        {
                            "sid": "SM123",
                            "num_media": "1",
                            "date_sent": "2022-11-16T12:00:00Z",
                            "subresource_uris": {"media": uri},
                        }
                    ]
                },
            )
            accounts.append({"sid": account, "subresource_uris": {"messages": messages_uri}})
        else:
            accounts.append({"sid": account, "subresource_uris": {stream: uri}})

        def response(request, context):
            query = parse_qs(urlparse(request.url).query)
            requests.append((urlparse(request.url).path, query))
            records = [{"sid": "recent", cursor: "2022-11-16T12:00:00Z"}]
            if query[lower_key][0] < datetime.fromisoformat(global_cursor).strftime(datetime_format):
                records.append({"sid": "historical", cursor: "2022-11-14T12:00:00Z"})
            return {body_key: records}

        requests_mock.get(f"https://api.twilio.com{uri}", json=response)
    requests_mock.get(f"{BASE}/Accounts.json", json={"accounts": accounts})
    state = (
        StateBuilder()
        .with_stream_state(
            stream,
            {"use_global_cursor": True, "state": {cursor: global_cursor}, "states": partitions, "lookback_window": 0},
        )
        .build()
    )
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    config = {**TEST_CONFIG, "start_date": "2022-11-14T00:00:00Z"}
    output = read(get_source(config, state), config, catalog, state)

    assert not output.errors
    statuses = ("init", "in-progress", "completed") if stream == "conferences" else (None,)

    def expected_requests(start, end="2022-11-16T12:03:11+00:00"):
        return [
            (
                f"/2010-04-01/Accounts/{account}/{resource}.json",
                {
                    lower_key: [start],
                    upper_key: [datetime.fromisoformat(end).strftime(datetime_format)],
                    "PageSize": ["1000"],
                    **({"Status": [status]} if status else {}),
                },
            )
            for account in ("AC123", "AC456")
            for status in statuses
        ]

    # Query dictionaries need a deterministic sort key for conferences' multiple statuses.
    key = lambda request: (request[0], str(sorted(request[1].items())))
    assert sorted(requests, key=key) == sorted(expected_requests(datetime.fromisoformat(global_cursor).strftime(datetime_format)), key=key)
    assert [record.record.data["sid"] for record in output.records] == ["recent"] * (2 * len(statuses))
    saved = output.most_recent_state.stream_state.__dict__
    assert saved["state"] == {cursor: datetime.fromisoformat("2022-11-16T12:00:00+00:00").strftime(datetime_format)}
    assert saved["use_global_cursor"] is True
    assert "states" not in saved

    requests.clear()
    resumed_state = StateBuilder().with_stream_state(stream, saved).build()
    with freeze_time("2022-11-17 12:03:11+00:00"):
        resumed = read(get_source(config, resumed_state), config, catalog, resumed_state)
    assert not resumed.errors
    assert sorted(requests, key=key) == sorted(expected_requests(saved["state"][cursor], "2022-11-17T12:03:11+00:00"), key=key)
    # The inclusive lower bound deliberately replays records at the cursor.
    assert [record.record.data["sid"] for record in resumed.records] == ["recent"] * (2 * len(statuses))
    assert resumed.most_recent_state.stream_state.__dict__["state"] == saved["state"]


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize(
    "global_mode,global_state,expected_start",
    [
        (False, {"date_sent": "2022-11-15T12:00:00Z"}, "2022-11-14 00:00:00Z"),
        (None, {"date_sent": "2022-11-15T12:00:00Z"}, "2022-11-14 00:00:00Z"),
        (True, {}, "2022-11-14 00:00:00Z"),
        (True, {"date_sent": "2022-11-15T12:00:00Z"}, "2022-11-15 11:49:00Z"),
    ],
)
def test_messages_preserves_partition_mode_and_lookback(requests_mock, global_mode, global_state, expected_start):
    partition_state = {
        "state": global_state,
        "states": [
            {
                "partition": {"subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json", "parent_slice": {}},
                "cursor": {"date_sent": "2022-11-14T00:00:00Z"},
            }
        ],
        "lookback_window": 60,
    }
    if global_mode is not None:
        partition_state["use_global_cursor"] = global_mode
    state = StateBuilder().with_stream_state("messages", partition_state).build()
    config = {**TEST_CONFIG, "start_date": "2022-11-13T00:00:00Z", "lookback_window": 10 if global_mode and global_state else 0}
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={"accounts": [{"sid": "AC123", "subresource_uris": {"messages": "/2010-04-01/Accounts/AC123/Messages.json"}}]},
    )
    requests = []

    def response(request, context):
        requests.append(parse_qs(urlparse(request.url).query))
        return {
            "messages": [
                {"sid": "overlap", "date_sent": expected_start.replace(" ", "T")},
                {"sid": "recent", "date_sent": "2022-11-16T12:00:00Z"},
            ]
        }

    requests_mock.get(f"{BASE}/Accounts/AC123/Messages.json", json=response)
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    output = read(get_source(config, state), config, catalog, state)

    assert not output.errors
    assert requests == [{"PageSize": ["1000"], "DateSent>": [expected_start], "DateSent<": ["2022-11-16 12:03:11Z"]}]
    assert [record.record.data["sid"] for record in output.records] == ["overlap", "recent"]
    saved = output.most_recent_state.stream_state.__dict__
    assert saved["state"] == {"date_sent": "2022-11-16 12:00:00Z"}
    if not global_mode:
        assert saved["states"] == [
            {
                "partition": {"subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json", "parent_slice": {}},
                "cursor": {"date_sent": "2022-11-16 12:00:00Z"},
            }
        ]
