# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.helpers import NOW, START, list_request, page, record, run


@pytest.mark.parametrize(
    "stream,path,cursor,incremental_parent",
    [
        ("invoices", "invoices", "updated_at", False),
        ("billing_infos", "accounts/account-1/billing_infos", "updated_at", True),
        ("account_coupon_redemptions", "accounts/account-1/coupon_redemptions", "updated_at", True),
        ("account_notes", "accounts/account-1/notes", "created_at", True),
        ("shipping_addresses", "accounts/account-1/shipping_addresses", "updated_at", False),
    ],
)
@pytest.mark.parametrize("suffix", ["", "Z", "+00:00"], ids=["legacy", "utc", "offset"])
@freeze_time(NOW)
def test_incremental_state_normalizes_legacy_cursor_and_resumes(stream, path, cursor, incremental_parent, suffix, monkeypatch, tmp_path):
    saved = "2026-01-07T13:19:48"
    latest = "2026-01-09T12:00:00Z"
    state = StateBuilder().with_stream_state(stream, {cursor: saved + suffix}).build()
    for begin, timestamp in [(saved + "Z", latest), (latest, latest)]:
        monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path / begin))
        with HttpMocker() as mocker:
            if stream != "invoices":
                parent_request = list_request("accounts", begin=begin if incremental_parent else START)
                mocker.get(parent_request, page([record("account-1", latest)]))
            request = list_request(path, begin=begin, sort=cursor)
            mocker.get(request, page([record("record-1", timestamp)]))
            output = run(stream, mode=SyncMode.incremental, state=state)
            mocker.assert_number_of_calls(request, 1)
            if stream != "invoices":
                mocker.assert_number_of_calls(parent_request, 1)
        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["record-1"]
        emitted = output.most_recent_state.stream_state.__dict__
        if stream == "invoices":
            assert emitted == {cursor: latest}
        else:
            assert emitted["states"] == [{"partition": {"account_id": "account-1", "parent_slice": {}}, "cursor": {cursor: latest}}]
        state = [output.state_messages[-1].state]
