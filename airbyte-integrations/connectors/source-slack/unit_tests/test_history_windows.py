# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import datetime
from copy import deepcopy

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source, get_stream_by_name


def config_for_window(token_config, days):
    return {
        **deepcopy(token_config),
        "start_date": "2025-12-26T00:00:00Z",
        "lookback_window": 0,
        "channel_messages_window_size": days,
        "threads_ignore_no_replies": True,
    }


@freeze_time("2026-10-14T00:00:00Z")
@pytest.mark.parametrize("days,expected_requests", [(100, 6), (365, 2)])
def test_quiet_thread_parents_need_fewer_history_requests(requests_mock, token_config, days, expected_requests):
    history = requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})
    stream = get_stream_by_name("threads", config_for_window(token_config, days))
    assert list(stream.generate_partitions()) == []
    assert history.call_count == expected_requests
    for channel in ["airbyte-for-beginners", "good-reads"]:
        calls = [r for r in history.request_history if r.qs["channel"] == [channel]]
        assert min(float(r.qs["oldest"][0]) for r in calls) == 1766707200.0
        assert max(float(r.qs["latest"][0]) for r in calls) == 1791936000.0


@freeze_time("2026-10-14T00:00:00Z")
@pytest.mark.parametrize("days", [100, 365])
def test_history_window_preserves_paginated_records(requests_mock, token_config, days):
    timestamps = [
        str(datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).timestamp())
        for d in ["2025-12-30T12:00:00", "2026-04-20T12:00:00", "2026-10-13T12:00:00"]
    ]

    def history(request, context):
        oldest, latest = float(request.qs["oldest"][0]), float(request.qs["latest"][0])
        eligible = sorted([ts for ts in timestamps if oldest <= float(ts) <= latest], reverse=True)
        offset = int(request.qs.get("cursor", ["0"])[0])
        page = eligible[offset : offset + 1]
        next_cursor = str(offset + 1) if offset + 1 < len(eligible) else ""
        return {
            "ok": True,
            "messages": [{"ts": ts, "text": "fixture"} for ts in page],
            "has_more": bool(next_cursor),
            "response_metadata": {"next_cursor": next_cursor},
        }

    endpoint = requests_mock.get("https://slack.com/api/conversations.history", json=history)
    config = config_for_window(token_config, days)
    state = StateBuilder().build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "channel_messages", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    output = read(get_source(config, "channel_messages", state), config=config, catalog=catalog, state=state)
    assert not output.errors
    assert {(r.record.data["channel_id"], r.record.data["ts"]) for r in output.records} == {
        (channel, ts) for channel in ["airbyte-for-beginners", "good-reads"] for ts in timestamps
    }
    if days == 365:
        assert any("cursor" in r.qs for r in endpoint.request_history)
