# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com"
ACCOUNT_IDS = ("AC123", "AC456")
GLOBAL_CURSOR = "2022-11-15T12:00:00Z"


def _read_messages(config, state=None, expecting_exception=False):
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    return read(get_source(config, state), config, catalog, state, expecting_exception)


def _register_messages(requests_mock):
    requests_mock.get(
        f"{BASE}/2010-04-01/Accounts.json",
        json={
            "accounts": [
                {
                    "sid": account_id,
                    "subresource_uris": {"messages": f"/2010-04-01/Accounts/{account_id}/Messages.json"},
                }
                for account_id in ACCOUNT_IDS
            ]
        },
    )
    captured = []

    def response(request, context):
        query = parse_qs(urlparse(request.url).query)
        captured.append((urlparse(request.url).path, query))
        lower = datetime.strptime(query["DateSent>"][0], "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
        upper = datetime.strptime(query["DateSent<"][0], "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
        path = urlparse(request.url).path
        account_id = path.split("/")[3]
        candidates = [
            {"sid": f"{account_id}-new", "date_sent": "2022-11-16T11:00:00Z"},
            {"sid": f"{account_id}-boundary", "date_sent": GLOBAL_CURSOR},
            {"sid": f"{account_id}-old", "date_sent": "2022-11-13T13:00:00Z"},
        ]
        records = [record for record in candidates if lower <= datetime.fromisoformat(record["date_sent"]) <= upper]
        if query.get("PageToken"):
            return {"messages": records[1:], "next_page_uri": None}
        next_query = {**query, "PageToken": ["next"], "Page": ["1"]}
        return {
            "messages": records[:1],
            "next_page_uri": f"{path}?{urlencode(next_query, doseq=True)}",
        }

    for account_id in ACCOUNT_IDS:
        requests_mock.get(f"{BASE}/2010-04-01/Accounts/{account_id}/Messages.json", json=response)
    return captured


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize("parent_slice", [None, {}], ids=["legacy-partitions", "nested-partitions"])
@pytest.mark.parametrize("use_global_cursor", [None, False, True], ids=["no-flag", "partition-mode", "global-mode"])
@pytest.mark.parametrize("lookback_minutes", [0, 60])
def test_messages_resume_from_global_checkpoint(requests_mock, parent_slice, use_global_cursor, lookback_minutes):
    captured = _register_messages(requests_mock)
    saved_state = {
        "state": {"date_sent": GLOBAL_CURSOR},
        "states": [
            {
                "partition": {"subresource_uri": f"/2010-04-01/Accounts/{account_id}/Messages.json"},
                "cursor": {"date_sent": "2022-11-13T12:00:00Z"},
            }
            for account_id in ACCOUNT_IDS
        ],
    }
    if parent_slice is not None:
        for partition in saved_state["states"]:
            partition["partition"]["parent_slice"] = deepcopy(parent_slice)
    if use_global_cursor is not None:
        saved_state["use_global_cursor"] = use_global_cursor
    state = StateBuilder().with_stream_state("messages", saved_state).build()
    config = {**TEST_CONFIG, "start_date": "2022-11-13T00:00:00Z", "lookback_window": lookback_minutes}
    output = _read_messages(config, state)

    lower = (datetime.fromisoformat(GLOBAL_CURSOR) - timedelta(minutes=lookback_minutes)).strftime("%Y-%m-%d %H:%M:%SZ")
    expected_queries = [
        {"DateSent>": [lower], "DateSent<": ["2022-11-16 12:03:11Z"], "PageSize": ["1000"]},
        {
            "DateSent>": [lower],
            "DateSent<": ["2022-11-16 12:03:11Z"],
            "PageSize": ["1000"],
            "PageToken": ["next"],
            "Page": ["1"],
        },
    ]
    for account_id in ACCOUNT_IDS:
        path = f"/2010-04-01/Accounts/{account_id}/Messages.json"
        assert [query for request_path, query in captured if request_path == path] == expected_queries
    assert not output.errors
    assert sorted(message.record.data["sid"] for message in output.records) == sorted(
        f"{account_id}-{suffix}" for account_id in ACCOUNT_IDS for suffix in ("boundary", "new")
    )
    checkpoint = output.most_recent_state.stream_state.__dict__
    assert checkpoint["state"] == {"date_sent": "2022-11-16 11:00:00Z"}
    assert checkpoint["use_global_cursor"] is True
    assert "states" not in checkpoint

    captured.clear()
    resumed_state = StateBuilder().with_stream_state("messages", checkpoint).build()
    resumed = _read_messages(config, resumed_state)
    resumed_lower = (
        datetime.fromisoformat(checkpoint["state"]["date_sent"])
        - timedelta(minutes=lookback_minutes, seconds=checkpoint["lookback_window"])
    ).strftime("%Y-%m-%d %H:%M:%SZ")
    assert len(captured) == 4
    assert all(query["DateSent>"] == [resumed_lower] for _, query in captured)
    assert sorted(message.record.data["sid"] for message in resumed.records) == [f"{account_id}-new" for account_id in ACCOUNT_IDS]
    assert resumed.most_recent_state.stream_state.__dict__["state"] == checkpoint["state"]


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize("state_shape", ["empty", "flat", "partition-only", "empty-partition-cursor"])
def test_messages_preserve_progress_without_global_checkpoint(requests_mock, state_shape):
    captured = _register_messages(requests_mock)
    config = {**TEST_CONFIG, "start_date": "2022-11-13T00:00:00Z"}
    expected_lowers = {account_id: "2022-11-13 00:00:00Z" for account_id in ACCOUNT_IDS}
    stream_state = {}
    if state_shape == "flat":
        stream_state = {"date_sent": GLOBAL_CURSOR}
        expected_lowers = {account_id: "2022-11-15 12:00:00Z" for account_id in ACCOUNT_IDS}
    elif state_shape in ("partition-only", "empty-partition-cursor"):
        stream_state = {
            "states": [
                {
                    "partition": {"subresource_uri": f"/2010-04-01/Accounts/{account_id}/Messages.json"},
                    "cursor": {"date_sent": cursor},
                }
                for account_id, cursor in zip(ACCOUNT_IDS, ("2022-11-13T12:00:00Z", GLOBAL_CURSOR))
            ],
        }
        expected_lowers = dict(zip(ACCOUNT_IDS, ("2022-11-13 12:00:00Z", "2022-11-15 12:00:00Z")))
        if state_shape == "empty-partition-cursor":
            stream_state["states"][0]["cursor"] = {}
            expected_lowers[ACCOUNT_IDS[0]] = "2022-11-13 00:00:00Z"
    state = StateBuilder().with_stream_state("messages", stream_state).build() if stream_state else None
    output = _read_messages(config, state)

    for account_id, lower in expected_lowers.items():
        queries = [query for path, query in captured if path == f"/2010-04-01/Accounts/{account_id}/Messages.json"]
        assert len(queries) == 2
        assert all(query["DateSent>"] == [lower] for query in queries)
    expected_ids = [f"{account_id}-{suffix}" for account_id in ACCOUNT_IDS for suffix in ("boundary", "new")]
    if state_shape != "flat":
        expected_ids.append("AC123-old")
        if state_shape == "empty":
            expected_ids.append("AC456-old")
    assert sorted(message.record.data["sid"] for message in output.records) == sorted(expected_ids)
    checkpoint = output.most_recent_state.stream_state.__dict__
    assert checkpoint["state"] == {"date_sent": "2022-11-16 11:00:00Z"}

    captured.clear()
    resumed_state = StateBuilder().with_stream_state("messages", checkpoint).build()
    resumed = _read_messages(config, resumed_state)
    assert len(captured) == 4
    assert all(query["DateSent>"] == ["2022-11-16 11:00:00Z"] for _, query in captured)
    assert sorted(message.record.data["sid"] for message in resumed.records) == [f"{account_id}-new" for account_id in ACCOUNT_IDS]
    resumed_checkpoint = resumed.most_recent_state.stream_state.__dict__
    assert resumed_checkpoint["state"] == checkpoint["state"]
    assert resumed_checkpoint["use_global_cursor"] is True
    assert "states" not in resumed_checkpoint


@freeze_time("2022-11-16 12:03:11+00:00")
def test_messages_do_not_advance_global_checkpoint_on_failure(requests_mock):
    captured = _register_messages(requests_mock)
    requests_mock.get(f"{BASE}/2010-04-01/Accounts/AC456/Messages.json", status_code=400, json={"message": "Invalid request"})
    stream_state = {
        "state": {"date_sent": GLOBAL_CURSOR},
        "states": [
            {
                "partition": {"subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json", "parent_slice": {}},
                "cursor": {"date_sent": "2022-11-13T12:00:00Z"},
            }
        ],
    }
    state = StateBuilder().with_stream_state("messages", stream_state).build()
    config = {**TEST_CONFIG, "start_date": "2022-11-13T00:00:00Z"}
    output = _read_messages(config, state, expecting_exception=True)

    assert output.errors
    assert len(captured) == 2
    assert all(query["DateSent>"] == ["2022-11-15 12:00:00Z"] for _, query in captured)
    assert sorted(message.record.data["sid"] for message in output.records) == ["AC123-boundary", "AC123-new"]
    checkpoints = [message.state.stream.stream_state.__dict__ for message in output.state_messages]
    assert checkpoints
    assert all(checkpoint["state"] == {"date_sent": "2022-11-15 12:00:00Z"} for checkpoint in checkpoints)
    assert all(checkpoint["use_global_cursor"] is True and "states" not in checkpoint for checkpoint in checkpoints)
