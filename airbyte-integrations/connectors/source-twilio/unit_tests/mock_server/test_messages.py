# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
GLOBAL_CURSOR = "2022-11-15T10:00:00Z"


def _read_messages(stream_state):
    state = StateBuilder().with_stream_state("messages", stream_state).build()
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    return read(get_source(TEST_CONFIG, state), TEST_CONFIG, catalog, state)


def _partition(account, cursor, parent_slice=True):
    partition = {"subresource_uri": f"/2010-04-01/Accounts/{account}/Messages.json"}
    if parent_slice:
        partition["parent_slice"] = {}
    return {"partition": partition, "cursor": {"date_sent": cursor}}


@freeze_time("2022-11-16 12:00:00+00:00")
@pytest.mark.parametrize("parent_slice", [False, True], ids=["legacy-partitions", "nested-partitions"])
@pytest.mark.parametrize("runtime_lookback", [0, 3600], ids=["no-overlap", "one-hour-overlap"])
def test_messages_resume_from_global_cursor(requests_mock, parent_slice, runtime_lookback):
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={
            "accounts": [
                {"sid": account, "subresource_uris": {"messages": f"/2010-04-01/Accounts/{account}/Messages.json"}}
                for account in ("AC123", "AC124")
            ]
        },
    )
    requests = []
    lower_bound = "2022-11-15 09:00:00Z" if runtime_lookback else "2022-11-15 10:00:00Z"

    def messages_response(request, context):
        query = parse_qs(urlparse(request.url).query)
        requests.append((urlparse(request.url).path, query))
        account = urlparse(request.url).path.split("/")[3]
        records = []
        if query["DateSent>"][0] < lower_bound:
            records.append({"sid": f"{account}-historical", "date_sent": "2022-11-14T11:00:00Z"})
        page = query.get("PageToken", ["first"])[0]
        if runtime_lookback and page == "first":
            records.append({"sid": f"{account}-overlap", "date_sent": "2022-11-15T09:30:00Z"})
        records.append({"sid": f"{account}-{page}", "date_sent": "2022-11-15T11:00:00Z"})
        return {
            "messages": records,
            "next_page_uri": (
                f"/2010-04-01/Accounts/{account}/Messages.json"
                f"?{urlencode({'DateSent>': lower_bound, 'DateSent<': '2022-11-16 12:00:00Z', 'PageSize': 1000, 'PageToken': 'second'})}"
                if page == "first"
                else None
            ),
        }

    for account in ("AC123", "AC124"):
        requests_mock.get(f"{BASE}/Accounts/{account}/Messages.json", json=messages_response)

    output = _read_messages(
        {
            "state": {"date_sent": GLOBAL_CURSOR},
            "states": [_partition(account, "2022-11-13T00:00:00Z", parent_slice) for account in ("AC123", "AC124")],
            "lookback_window": runtime_lookback,
        }
    )

    expected_ids = [
        "AC123-first",
        "AC123-second",
        "AC124-first",
        "AC124-second",
    ]
    if runtime_lookback:
        expected_ids.extend(["AC123-overlap", "AC124-overlap"])
    assert sorted(record.record.data["sid"] for record in output.records) == sorted(expected_ids)
    request_key = lambda item: (item[0], item[1].get("PageToken", [""])[0])
    assert sorted(requests, key=request_key) == sorted(
        [
            (
                f"/2010-04-01/Accounts/{account}/Messages.json",
                {
                    "DateSent>": [lower_bound],
                    "DateSent<": ["2022-11-16 12:00:00Z"],
                    "PageSize": ["1000"],
                    **({"PageToken": ["second"]} if page == "second" else {}),
                },
            )
            for account in ("AC123", "AC124")
            for page in ("first", "second")
        ],
        key=request_key,
    )
    checkpoint = output.most_recent_state.stream_state.__dict__
    assert checkpoint["state"] == {"date_sent": "2022-11-15 11:00:00Z"}
    assert checkpoint["use_global_cursor"] is True
    assert not checkpoint.get("states")

    requests.clear()

    def resumed_response(request, context):
        query = parse_qs(urlparse(request.url).query)
        requests.append((urlparse(request.url).path, query))
        account = urlparse(request.url).path.split("/")[3]
        return {"messages": [{"sid": f"{account}-new-message", "date_sent": "2022-11-15T11:30:00Z"}]}

    for account in ("AC123", "AC124"):
        requests_mock.get(f"{BASE}/Accounts/{account}/Messages.json", json=resumed_response)
    resumed = _read_messages(checkpoint)
    assert sorted(record.record.data["sid"] for record in resumed.records) == ["AC123-new-message", "AC124-new-message"]
    assert len(requests) == 2
    assert all(
        query == {"DateSent>": ["2022-11-15 11:00:00Z"], "DateSent<": ["2022-11-16 12:00:00Z"], "PageSize": ["1000"]}
        for _, query in requests
    )
    assert resumed.most_recent_state.stream_state.__dict__["state"] == {"date_sent": "2022-11-15 11:30:00Z"}


@freeze_time("2022-11-16 12:00:00+00:00")
@pytest.mark.parametrize(
    "stream_state",
    [
        {"date_sent": GLOBAL_CURSOR},
        {"state": {"date_sent": GLOBAL_CURSOR}, "use_global_cursor": False},
        {
            "states": [
                _partition("AC123", GLOBAL_CURSOR, False),
                _partition("AC124", "2022-11-14T10:00:00Z"),
            ]
        },
    ],
    ids=["flat-cursor", "global-only", "partition-only"],
)
def test_messages_legacy_state_survives_empty_read(requests_mock, stream_state):
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={
            "accounts": [
                {"sid": account, "subresource_uris": {"messages": f"/2010-04-01/Accounts/{account}/Messages.json"}}
                for account in ("AC123", "AC124")
            ]
        },
    )
    matchers = [requests_mock.get(f"{BASE}/Accounts/{account}/Messages.json", json={"messages": []}) for account in ("AC123", "AC124")]
    output = _read_messages(stream_state)
    assert not output.records
    assert [parse_qs(urlparse(matcher.last_request.url).query)["DateSent>"] for matcher in matchers] == [
        ["2022-11-15 10:00:00Z"],
        ["2022-11-14 10:00:00Z"] if "states" in stream_state else ["2022-11-15 10:00:00Z"],
    ]
    checkpoint = output.most_recent_state.stream_state.__dict__
    partition_only = "states" in stream_state
    if partition_only:
        assert sorted(state["cursor"]["date_sent"] for state in checkpoint["states"]) == [
            "2022-11-14 10:00:00Z",
            "2022-11-15 10:00:00Z",
        ]
    else:
        assert checkpoint["state"] == {"date_sent": "2022-11-15 10:00:00Z"}

    resumed = _read_messages(checkpoint)
    resumed_checkpoint = resumed.most_recent_state.stream_state.__dict__
    if partition_only:
        assert resumed_checkpoint["states"] == checkpoint["states"]
    else:
        assert resumed_checkpoint["use_global_cursor"] is True
        assert not resumed_checkpoint.get("states")
        assert resumed_checkpoint["state"] == {"date_sent": "2022-11-15 10:00:00Z"}
