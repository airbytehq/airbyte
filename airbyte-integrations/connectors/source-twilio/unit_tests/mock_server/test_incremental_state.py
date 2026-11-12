# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import copy
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
ACCOUNT_IDS = ("AC123", "AC456")


@pytest.mark.parametrize(
    "stream_name,resource,cursor_field", [("messages", "Messages", "date_sent"), ("recordings", "Recordings", "date_created")]
)
@pytest.mark.parametrize("legacy_partition", [False, True])
@pytest.mark.parametrize("lookback_minutes", [0, 60])
def test_global_state_does_not_replay_stale_partitions(
    requests_mock, stream_name, resource, cursor_field, legacy_partition, lookback_minutes
):
    config = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z", "lookback_window": lookback_minutes}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={
            "accounts": [
                {"sid": sid, "subresource_uris": {stream_name: f"/2010-04-01/Accounts/{sid}/{resource}.json"}} for sid in ACCOUNT_IDS
            ]
        },
    )
    child_requests = []
    records_by_account = {
        sid: [
            {"sid": f"{sid}-old", cursor_field: "2022-11-15T12:00:00Z"},
            {"sid": f"{sid}-lookback", cursor_field: "2022-11-15T23:30:00Z"},
            {"sid": f"{sid}-boundary", cursor_field: "2022-11-16T00:00:00Z"},
            {"sid": f"{sid}-new", cursor_field: "2022-11-16T12:00:00Z"},
        ]
        for sid in ACCOUNT_IDS
    }
    lower_key = "DateSent>" if stream_name == "messages" else "DateCreated>"
    upper_key = "DateSent<" if stream_name == "messages" else "DateCreated<"

    def response(request, context):
        query = parse_qs(urlparse(request.url).query)
        account = urlparse(request.url).path.split("/")[3]
        child_requests.append((account, query))
        lower = query[lower_key][0].replace(" ", "T")
        upper = query[upper_key][0].replace(" ", "T")
        return {stream_name: [record for record in records_by_account[account] if lower <= record[cursor_field] <= upper]}

    for sid in ACCOUNT_IDS:
        requests_mock.get(f"{BASE}/Accounts/{sid}/{resource}.json", json=response)

    with freeze_time("2022-11-16T00:00:00Z"):
        first = read(get_source(config), config, catalog)
    assert not first.errors
    assert sorted(message.record.data["sid"] for message in first.records) == sorted(
        f"{sid}-{suffix}" for sid in ACCOUNT_IDS for suffix in ("old", "lookback", "boundary")
    )
    persisted_state = copy.deepcopy(first.most_recent_state.stream_state.__dict__)
    assert persisted_state["state"] == {cursor_field: "2022-11-16 00:00:00Z"}
    persisted_state["use_global_cursor"] = True
    for partition_state in persisted_state["states"]:
        partition_state["cursor"] = {cursor_field: "2022-11-15T00:00:00Z"}
        if legacy_partition:
            partition_state["partition"].pop("parent_slice")
    state = StateBuilder().with_stream_state(stream_name, persisted_state).build()
    child_requests.clear()

    with freeze_time("2022-11-17T00:00:00Z"):
        resumed = read(get_source(config, state), config, catalog, state)

    assert not resumed.errors
    assert sorted(child_requests) == [
        (
            sid,
            {
                lower_key: ["2022-11-15 23:00:00Z" if lookback_minutes else "2022-11-16 00:00:00Z"],
                upper_key: ["2022-11-17 00:00:00Z"],
                "PageSize": ["1000"],
            },
        )
        for sid in ACCOUNT_IDS
    ]
    assert sorted(message.record.data["sid"] for message in resumed.records) == sorted(
        f"{sid}-{suffix}"
        for sid in ACCOUNT_IDS
        for suffix in (("lookback", "boundary", "new") if lookback_minutes else ("boundary", "new"))
    )
    resumed_state = resumed.most_recent_state.stream_state.__dict__
    assert resumed_state["state"] == {cursor_field: "2022-11-16 12:00:00Z"}
    assert resumed_state["use_global_cursor"] is True
    assert not resumed_state.get("states")

    state = StateBuilder().with_stream_state(stream_name, resumed_state).build()
    child_requests.clear()
    with freeze_time("2022-11-18T00:00:00Z"):
        third = read(get_source(config, state), config, catalog, state)
    assert not third.errors
    assert sorted(message.record.data["sid"] for message in third.records) == [f"{sid}-new" for sid in ACCOUNT_IDS]
    assert sorted(child_requests) == [
        (
            sid,
            {
                lower_key: ["2022-11-16 11:00:00Z" if lookback_minutes else "2022-11-16 12:00:00Z"],
                upper_key: ["2022-11-18 00:00:00Z"],
                "PageSize": ["1000"],
            },
        )
        for sid in ACCOUNT_IDS
    ]
    assert third.most_recent_state.stream_state.__dict__["state"] == {cursor_field: "2022-11-16 12:00:00Z"}
