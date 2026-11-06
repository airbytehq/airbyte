# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


@freeze_time("2025-08-20T00:00:00Z")
@pytest.mark.parametrize("interrupted", [False, True])
def test_threads_resume_from_emitted_parent_state(requests_mock, token_config, interrupted):
    config = {
        **token_config,
        "start_date": "2025-08-01T00:00:00Z",
        "end_date": "2025-08-20T00:00:00Z",
        "lookback_window": 7,
        "channel_filter": [],
    }
    messages = {"airbyte-for-beginners": "1755475200.000001", "good-reads": "1755561600.000002"}

    def history_response(request, context):
        return {"ok": True, "messages": [{"ts": messages[request.qs["channel"][0]], "reply_count": 1}]}

    def replies_response(request, context):
        return {"ok": True, "messages": [{"ts": request.qs["ts"][0]}]}

    requests_mock.get("https://slack.com/api/conversations.history", json=history_response)
    requests_mock.get("https://slack.com/api/conversations.replies", json=replies_response)
    catalog = CatalogBuilder().with_stream("threads", SyncMode.incremental).build()
    first = read(get_source(config, "threads"), config=config, catalog=catalog)
    assert len(first.records) == 2
    saved = deepcopy(first.most_recent_state.stream_state.__dict__)
    if interrupted:
        saved["states"] = []
        saved.pop("state", None)
    state = StateBuilder().with_stream_state("threads", saved).build()
    history_count = len(requests_mock.request_history)
    second = read(get_source(config, "threads", state), config=config, catalog=catalog, state=state)
    resumed = [request.qs for request in requests_mock.request_history[history_count:] if request.path.endswith("conversations.history")]
    assert sorted(resumed, key=lambda query: query["channel"]) == [
        {
            "inclusive": ["true"],
            "limit": ["1000"],
            "channel": [channel],
            "oldest": [str(float(timestamp) - 7 * 86400)],
            "latest": ["1755648000.0"],
        }
        for channel, timestamp in sorted(messages.items())
    ]
    assert {r.record.data["channel_id"] for r in second.records} == set(messages)
    assert len(second.records) == 2
    assert second.most_recent_state.stream_state.__dict__["parent_state"] == saved["parent_state"]
