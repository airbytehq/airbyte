# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .helpers import config, read_stream, request


@pytest.mark.parametrize("legacy_dates", [False, True])
@pytest.mark.parametrize(
    "mode,prior_cursor", [(SyncMode.full_refresh, None), (SyncMode.incremental, None), (SyncMode.incremental, "02-11-2026")]
)
@pytest.mark.parametrize("empty", [False, True])
def test_history_daily_slices(legacy_dates: bool, mode: SyncMode, prior_cursor: str | None, empty: bool) -> None:
    state = StateBuilder().with_stream_state("history", {"date": prior_cursor}).build() if prior_cursor else None
    dates = ["02-11-2026", "03-11-2026"] if prior_cursor else ["01-11-2026", "02-11-2026", "03-11-2026"]
    expected_records = []
    with HttpMocker() as mocker:
        requests = []
        for index, date in enumerate(dates):
            expected_request = request("history", date=date)
            requests.append(expected_request)
            payload = {"id": "bitcoin", "symbol": "btc", "market_data": {"current_price": {"usd": 69000 + index}}}
            mocker.get(expected_request, HttpResponse(json.dumps([] if empty else payload), 200))
            if not empty:
                expected_records.append({**payload, "date": date})
        output = read_stream("history", config(legacy_dates=legacy_dates), mode, state)
        assert sorted((message.record.data for message in output.records), key=lambda record: record["date"]) == expected_records
        expected_cursor = (prior_cursor or "01-11-2026") if empty else "03-11-2026"
        assert output.most_recent_state.stream_state.__dict__ == {"date": expected_cursor}
        assert output.errors == []
        for expected_request in requests:
            mocker.assert_number_of_calls(expected_request, 1)
