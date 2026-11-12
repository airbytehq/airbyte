# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"


@pytest.fixture
def requests_mock_case_sensitive() -> bool:
    return True


def record_ids(output: EntrypointOutput) -> Counter[str]:
    ids = []
    for message in output.records:
        assert message.record is not None
        ids.append(message.record.data["sid"])
    return Counter(ids)


@pytest.mark.parametrize(
    "stream,cursor,filter_name", [("messages", "date_sent", "DateSent"), ("recordings", "date_created", "DateCreated")]
)
@pytest.mark.parametrize("lookback_minutes", [0, 60])
def test_incremental_state_advances_across_windows(
    requests_mock, stream: str, cursor: str, filter_name: str, lookback_minutes: int
) -> None:
    config = {**TEST_CONFIG, "start_date": "2022-11-13T00:00:00Z", "slice_step_duration": "P1D", "lookback_window": lookback_minutes}
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    account_cursors = {"AC123": "2022-11-16T11:00:00Z", "AC456": "2022-11-15T18:00:00Z"}
    accounts = [
        {"sid": account, "subresource_uris": {stream: f"/2010-04-01/Accounts/{account}/{stream.title()}.json"}}
        for account in account_cursors
    ]
    requests_mock.get(f"{BASE}/Accounts.json", json={"accounts": accounts})
    requests = []
    records = {}
    for account, latest in account_cursors.items():
        dates = ["2022-11-13T12:00:00Z", "2022-11-13T23:59:59Z", "2022-11-14T00:00:00Z", "2022-11-14T00:00:00Z", latest]
        records[account] = [{"sid": f"{account}-{index}", cursor: date} for index, date in enumerate(dates)]

    def response(request, context):
        url = urlparse(request.url)
        account = url.path.split("/")[3]
        query = {key: values[0] for key, values in parse_qs(url.query).items()}
        requests.append((account, query))
        lower = query[f"{filter_name}>"]
        upper = query[f"{filter_name}<"]
        matching = [record for record in records[account] if lower <= record[cursor].replace("T", " ") <= upper]
        offset = int(query.get("PageToken", "0"))
        page = matching[offset : offset + 1]
        next_page = None
        if offset + 1 < len(matching):
            next_page = f"{url.path}?{urlencode({**query, 'PageToken': str(offset + 1)})}"
        return {stream: page, "next_page_uri": next_page}

    for account in account_cursors:
        requests_mock.get(f"{BASE}/Accounts/{account}/{stream.title()}.json", json=response)

    with freeze_time("2022-11-16T12:03:11Z"):
        first = read(get_source(config), config, catalog)

    assert not first.errors
    assert record_ids(first) == Counter(record["sid"] for account_records in records.values() for record in account_records)
    expected_windows = [
        ("2022-11-13 00:00:00Z", "2022-11-13 23:59:59Z"),
        ("2022-11-14 00:00:00Z", "2022-11-14 23:59:59Z"),
        ("2022-11-15 00:00:00Z", "2022-11-15 23:59:59Z"),
        ("2022-11-16 00:00:00Z", "2022-11-16 12:03:11Z"),
    ]
    for account in account_cursors:
        assert Counter(
            tuple(sorted(query.items()))
            for requested_account, query in requests
            if requested_account == account and "PageToken" not in query
        ) == Counter(
            tuple(sorted({f"{filter_name}>": start, f"{filter_name}<": end, "PageSize": "1000"}.items())) for start, end in expected_windows
        )
        assert sum("PageToken" in query for requested_account, query in requests if requested_account == account) == 2

    first_state = first.most_recent_state
    assert first_state is not None
    saved_state = first_state.stream_state.__dict__
    state = StateBuilder().with_stream_state(stream, saved_state).build()
    requests.clear()
    for account, latest in account_cursors.items():
        date = datetime.fromisoformat(latest.replace("Z", "+00:00"))
        records[account].extend(
            [
                {"sid": f"{account}-lookback", cursor: (date - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")},
                {"sid": f"{account}-new", cursor: "2022-11-17T10:00:00Z"},
            ]
        )
    with freeze_time("2022-11-17T12:03:11Z"):
        second = read(get_source(config, state), config, catalog, state)

    assert not second.errors
    expected_ids = [f"{account}-{suffix}" for account in account_cursors for suffix in ("4", "new")]
    if lookback_minutes:
        expected_ids.extend(f"{account}-lookback" for account in account_cursors)
    assert record_ids(second) == Counter(expected_ids)
    assert {state["partition"]["subresource_uri"].split("/")[3]: state["cursor"][cursor] for state in saved_state["states"]} == {
        account: date.replace("T", " ") for account, date in account_cursors.items()
    }
    for account, latest in account_cursors.items():
        lower = (datetime.fromisoformat(latest.replace("Z", "+00:00")) - timedelta(minutes=lookback_minutes)).strftime("%Y-%m-%d %H:%M:%SZ")
        assert min(query[f"{filter_name}>"] for requested_account, query in requests if requested_account == account) == lower
    second_state = second.most_recent_state
    assert second_state is not None
    resumed_state = second_state.stream_state.__dict__
    assert [state["cursor"][cursor] for state in resumed_state["states"]] == ["2022-11-17 10:00:00Z"] * 2
