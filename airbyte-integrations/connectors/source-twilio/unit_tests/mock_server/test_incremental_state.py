# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
ACCOUNTS = ("AC123", "AC456")
GLOBAL_CURSOR = "2022-11-15T12:00:00Z"
STALE_CURSOR = "2022-11-13T12:00:00Z"


def _read_messages(state, lookback_minutes):
    config = {**TEST_CONFIG, "start_date": "2022-11-12T00:00:00Z", "lookback_window": lookback_minutes}
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    return read(get_source(config, state), config, catalog, state)


def _mock_accounts(requests_mock):
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={
            "accounts": [
                {"sid": account, "subresource_uris": {"messages": f"/2010-04-01/Accounts/{account}/Messages.json"}} for account in ACCOUNTS
            ]
        },
    )


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize("legacy_partition", [False, True])
@pytest.mark.parametrize("lookback_minutes", [0, 60])
def test_messages_global_cursor_ignores_stale_partitions(requests_mock, legacy_partition, lookback_minutes):
    _mock_accounts(requests_mock)
    state = (
        StateBuilder()
        .with_stream_state(
            "messages",
            {
                "use_global_cursor": True,
                "state": {"date_sent": GLOBAL_CURSOR},
                "lookback_window": 0,
                "parent_state": {},
                "states": [
                    {
                        "partition": {
                            "subresource_uri": f"/2010-04-01/Accounts/{account}/Messages.json",
                            **({} if legacy_partition else {"parent_slice": {}}),
                        },
                        "cursor": {"date_sent": STALE_CURSOR},
                    }
                    for account in ACCOUNTS
                ],
            },
        )
        .build()
    )
    for account in ACCOUNTS:
        records = [
            {"sid": f"{account}-historical", "date_sent": STALE_CURSOR},
            {"sid": f"{account}-overlap", "date_sent": "2022-11-15T11:30:00Z"},
            {"sid": f"{account}-new", "date_sent": "2022-11-16T01:00:00Z"},
        ]

        def messages_response(request, context, records=records):
            query = parse_qs(urlparse(request.url).query)
            lower = datetime.strptime(query["DateSent>"][0], "%Y-%m-%d %H:%M:%SZ")
            upper = datetime.strptime(query["DateSent<"][0], "%Y-%m-%d %H:%M:%SZ")
            return {
                "messages": [record for record in records if lower <= datetime.strptime(record["date_sent"], "%Y-%m-%dT%H:%M:%SZ") <= upper]
            }

        requests_mock.get(
            f"{BASE}/Accounts/{account}/Messages.json",
            json=messages_response,
        )

    output = _read_messages(state, lookback_minutes)

    lower = datetime(2022, 11, 15, 12) - timedelta(minutes=lookback_minutes)
    expected_query = {
        "DateSent>": [lower.strftime("%Y-%m-%d %H:%M:%SZ")],
        "DateSent<": ["2022-11-16 12:03:11Z"],
        "PageSize": ["1000"],
    }
    message_requests = [request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/Messages.json")]
    assert sorted((urlparse(request.url).path, parse_qs(urlparse(request.url).query)) for request in message_requests) == [
        (f"/2010-04-01/Accounts/{account}/Messages.json", expected_query) for account in ACCOUNTS
    ]
    expected_ids = [f"{account}-{suffix}" for account in ACCOUNTS for suffix in (["overlap", "new"] if lookback_minutes else ["new"])]
    assert sorted(record.record.data["sid"] for record in output.records) == sorted(expected_ids)
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state["use_global_cursor"] is True
    assert final_state["state"] == {"date_sent": "2022-11-16 01:00:00Z"}
    assert not final_state.get("states")

    resumed_state = StateBuilder().with_stream_state("messages", final_state).build()
    requests_mock.reset_mock()
    resumed = _read_messages(resumed_state, lookback_minutes)
    resumed_requests = [request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/Messages.json")]
    resumed_lower = datetime(2022, 11, 16, 1) - timedelta(minutes=lookback_minutes)
    expected_query["DateSent>"] = [resumed_lower.strftime("%Y-%m-%d %H:%M:%SZ")]
    assert sorted((urlparse(request.url).path, parse_qs(urlparse(request.url).query)) for request in resumed_requests) == [
        (f"/2010-04-01/Accounts/{account}/Messages.json", expected_query) for account in ACCOUNTS
    ]
    # The API's inclusive boundary can return the latest record again on resume.
    assert sorted(record.record.data["sid"] for record in resumed.records) == [f"{account}-new" for account in ACCOUNTS]
