#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import copy
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"


@freeze_time("2022-11-16 12:00:00+00:00")
@pytest.mark.parametrize(
    "stream,resource,cursor,lower,upper",
    [
        ("messages", "Messages", "date_sent", "DateSent>", "DateSent<"),
        ("recordings", "Recordings", "date_created", "DateCreated>", "DateCreated<"),
        ("calls", "Calls", "end_time", "EndTime>", "EndTime<"),
    ],
)
@pytest.mark.parametrize("lookback_minutes", [0, 60])
@pytest.mark.parametrize("legacy_partition", [False, True])
def test_stale_partition_uses_global_checkpoint(requests_mock, stream, resource, cursor, lower, upper, lookback_minutes, legacy_partition):
    config = {**TEST_CONFIG, "start_date": "2022-11-10T00:00:00Z", "lookback_window": lookback_minutes}
    runtime_lookback_seconds = 0 if stream == "calls" else 120

    def partition(sid):
        value = {"subresource_uri": f"/2010-04-01/Accounts/{sid}/{resource}.json"}
        if not legacy_partition:
            value["parent_slice"] = {}
        return value

    state = (
        StateBuilder()
        .with_stream_state(
            stream,
            {
                "states": [
                    {"partition": partition("AC123"), "cursor": {cursor: "2022-11-10T00:00:00Z"}},
                    {"partition": partition("AC456"), "cursor": {cursor: "2022-11-15T00:00:00Z"}},
                ],
                "state": {cursor: "2022-11-14T00:00:00Z"},
                "lookback_window": runtime_lookback_seconds,
                "use_global_cursor": False,
            },
        )
        .build()
    )
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={"accounts": [{"sid": sid, "subresource_uris": {stream: partition(sid)["subresource_uri"]}} for sid in ("AC123", "AC456")]},
    )
    requests = []
    records_by_account = {
        "AC123": [
            {"sid": "old", cursor: "2022-11-11T00:00:00Z"},
            {"sid": "boundary", cursor: "2022-11-14T00:00:00Z"},
            {"sid": "new-123", cursor: "2022-11-15T12:00:00Z"},
        ],
        "AC456": [{"sid": "new-456", cursor: "2022-11-15T12:00:00Z"}],
    }

    def response(request, context):
        query = parse_qs(urlparse(request.url).query)
        path = urlparse(request.url).path
        requests.append((path, query))
        start = datetime.fromisoformat(query[lower][0].replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        return {
            stream: [
                record
                for record in records_by_account[path.split("/")[3]]
                if datetime.fromisoformat(record[cursor].replace("Z", "+00:00")) >= start
            ]
        }

    for sid in ("AC123", "AC456"):
        requests_mock.get(f"{BASE}/Accounts/{sid}/{resource}.json", json=response)
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    output = read(get_source(config, state), config, catalog, state)
    assert not output.errors
    date_format = "%Y-%m-%d" if stream == "calls" else "%Y-%m-%d %H:%M:%SZ"
    expected_starts = {
        sid: (
            datetime.fromisoformat(start) - timedelta(minutes=lookback_minutes, seconds=runtime_lookback_seconds if sid == "AC123" else 0)
        ).strftime(date_format)
        for sid, start in [("AC123", "2022-11-14T00:00:00"), ("AC456", "2022-11-15T00:00:00")]
    }
    for sid, expected_start in expected_starts.items():
        actual = [query for path, query in requests if f"/{sid}/" in path]
        assert actual == [
            {
                lower: [expected_start],
                upper: ["2022-11-16" if stream == "calls" else "2022-11-16 12:00:00Z"],
                "PageSize": ["1000"],
            }
        ]
    assert sorted(record.record.data["sid"] for record in output.records) == ["boundary", "new-123", "new-456"]
    saved = copy.deepcopy(output.most_recent_state.stream_state.__dict__)
    expected_cursor = "2022-11-15" if stream == "calls" else "2022-11-15 12:00:00Z"
    assert saved["state"][cursor] == expected_cursor
    assert all(entry["cursor"][cursor] == expected_cursor for entry in saved["states"])
    requests.clear()
    resumed_state = StateBuilder().with_stream_state(stream, saved).build()
    resumed = read(get_source(config, resumed_state), config, catalog, resumed_state)
    assert not resumed.errors
    resumed_start = (datetime(2022, 11, 15, 0 if stream == "calls" else 12) - timedelta(minutes=lookback_minutes)).strftime(date_format)
    assert sorted(requests) == sorted(
        [
            (
                f"/2010-04-01/Accounts/{sid}/{resource}.json",
                {
                    lower: [resumed_start],
                    upper: ["2022-11-16" if stream == "calls" else "2022-11-16 12:00:00Z"],
                    "PageSize": ["1000"],
                },
            )
            for sid in ("AC123", "AC456")
        ]
    )
    expected_resumed_ids = ["new-123", "new-456"]
    if stream == "calls" and lookback_minutes:
        expected_resumed_ids.insert(0, "boundary")
    assert sorted(record.record.data["sid"] for record in resumed.records) == expected_resumed_ids
    assert resumed.most_recent_state.stream_state.__dict__["state"][cursor] == expected_cursor
