# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
CONFIG = {**TEST_CONFIG, "start_date": "2022-08-01T00:00:00Z"}

# stream name -> (resource file, cursor field, lower bound parameter, upper bound parameter)
STREAMS = {
    "messages": ("Messages.json", "date_sent", "DateSent>", "DateSent<"),
    "recordings": ("Recordings.json", "date_created", "DateCreated>", "DateCreated<"),
}


def _partition(stream_name, account_sid="AC123"):
    return {"subresource_uri": f"/2010-04-01/Accounts/{account_sid}/{STREAMS[stream_name][0]}", "parent_slice": {}}


def _sync(requests_mock, stream_name, now, state=None, records_by_window_start=None, account_sids=("AC123",)):
    """Run one incremental read. Returns (requested windows per account, emitted record sids, final stream state)."""
    resource, cursor_field, lower_key, upper_key = STREAMS[stream_name]
    records_by_window_start = records_by_window_start or {}
    windows = {sid: [] for sid in account_sids}

    accounts = [{"sid": sid, "subresource_uris": {stream_name: f"/2010-04-01/Accounts/{sid}/{resource}"}} for sid in account_sids]
    requests_mock.get(f"{BASE}/Accounts.json", json={"accounts": accounts})

    def _register(account_sid):
        def _callback(request, context):
            query = parse_qs(urlparse(request.url).query)
            lower = query[lower_key][0]
            windows[account_sid].append((lower, query[upper_key][0]))
            return {stream_name: [{"sid": sid, cursor_field: value} for sid, value in records_by_window_start.get(lower, [])]}

        requests_mock.get(f"{BASE}/Accounts/{account_sid}/{resource}", json=_callback)

    for account_sid in account_sids:
        _register(account_sid)

    input_state = StateBuilder().with_stream_state(stream_name, state).build() if state else None
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with freeze_time(now):
        output = read(get_source(CONFIG, input_state), CONFIG, catalog, input_state)

    assert output.errors == []
    final_state = json.loads(json.dumps(output.most_recent_state.stream_state.__dict__, default=lambda o: o.__dict__))
    return {sid: sorted(w) for sid, w in windows.items()}, sorted(r.record.data["sid"] for r in output.records), final_state


@pytest.mark.parametrize("stream_name", list(STREAMS))
def test_second_sync_resumes_from_latest_record_after_multi_window_first_sync(stream_name, requests_mock):
    cursor_field = STREAMS[stream_name][1]
    first_sync_records = {
        "2022-08-01 00:00:00Z": [("R-AUG", "2022-08-03T00:00:00Z")],
        "2022-09-01 00:00:00Z": [("R-SEP", "2022-09-03T00:00:00Z")],
        "2022-10-01 00:00:00Z": [("R-OCT", "2022-10-03T00:00:00Z")],
        "2022-11-01 00:00:00Z": [("R-NOV", "2022-11-03T00:00:00Z")],
    }

    windows, sids, state = _sync(requests_mock, stream_name, "2022-11-16 12:03:11+00:00", records_by_window_start=first_sync_records)

    assert windows["AC123"] == [
        ("2022-08-01 00:00:00Z", "2022-08-31 23:59:59Z"),
        ("2022-09-01 00:00:00Z", "2022-09-30 23:59:59Z"),
        ("2022-10-01 00:00:00Z", "2022-10-31 23:59:59Z"),
        ("2022-11-01 00:00:00Z", "2022-11-16 12:03:11Z"),
    ]
    assert sids == ["R-AUG", "R-NOV", "R-OCT", "R-SEP"]
    assert state["states"] == [{"partition": _partition(stream_name), "cursor": {cursor_field: "2022-11-03 00:00:00Z"}}]
    assert state["state"] == {cursor_field: "2022-11-03 00:00:00Z"}

    # The lower bound is inclusive of the saved cursor, so the latest record of the first sync is the only overlap.
    second_sync_records = {"2022-11-03 00:00:00Z": [("R-NOV", "2022-11-03T00:00:00Z"), ("R-NEW", "2022-11-17T08:00:00Z")]}
    windows, sids, state = _sync(
        requests_mock, stream_name, "2022-11-17 12:03:11+00:00", state=state, records_by_window_start=second_sync_records
    )

    assert windows["AC123"] == [("2022-11-03 00:00:00Z", "2022-11-17 12:03:11Z")]
    assert sids == ["R-NEW", "R-NOV"]
    assert state["states"] == [{"partition": _partition(stream_name), "cursor": {cursor_field: "2022-11-17 08:00:00Z"}}]
    assert state["state"] == {cursor_field: "2022-11-17 08:00:00Z"}


@pytest.mark.parametrize("stream_name", list(STREAMS))
@pytest.mark.parametrize(
    "partition_cursor,lookback_window,expected_lower_bound",
    [
        pytest.param("2022-08-03 00:00:00Z", 0, "2022-11-03 00:00:00Z", id="stale_partition_resumes_from_stream_cursor"),
        pytest.param("2022-08-03T00:00:00Z", 90, "2022-11-02 23:58:30Z", id="stale_partition_resumes_from_stream_cursor_minus_lookback"),
        pytest.param("2022-11-10 00:00:00Z", 0, "2022-11-10 00:00:00Z", id="partition_ahead_of_stream_cursor_is_kept"),
    ],
)
def test_state_with_partition_cursor_behind_stream_cursor(
    stream_name, partition_cursor, lookback_window, expected_lower_bound, requests_mock
):
    """State shape written by versions that left the partition cursor at the first request window."""
    cursor_field = STREAMS[stream_name][1]
    state = {
        "use_global_cursor": False,
        "states": [{"partition": _partition(stream_name), "cursor": {cursor_field: partition_cursor}}],
        "state": {cursor_field: "2022-11-03 00:00:00Z"},
        "lookback_window": lookback_window,
        "parent_state": {},
    }
    records = {expected_lower_bound: [("R-NEW", "2022-11-17T08:00:00Z")]}

    windows, sids, final_state = _sync(
        requests_mock,
        stream_name,
        "2022-11-17 12:03:11+00:00",
        state=state,
        records_by_window_start=records,
        account_sids=("AC123", "AC456"),
    )

    assert windows["AC123"] == [(expected_lower_bound, "2022-11-17 12:03:11Z")]
    # A partition without saved state falls back to the stream cursor minus the saved lookback, as before.
    fallback_lower_bound = "2022-11-02 23:58:30Z" if lookback_window else "2022-11-03 00:00:00Z"
    assert windows["AC456"] == [(fallback_lower_bound, "2022-11-17 12:03:11Z")]
    # The mocked record is served for the window starting at `expected_lower_bound`, in whichever account requests it.
    assert sids == ["R-NEW"] * sum(account_windows[0][0] == expected_lower_bound for account_windows in windows.values())
    assert final_state["states"][0] == {"partition": _partition(stream_name), "cursor": {cursor_field: "2022-11-17 08:00:00Z"}}
    assert final_state["state"] == {cursor_field: "2022-11-17 08:00:00Z"}
