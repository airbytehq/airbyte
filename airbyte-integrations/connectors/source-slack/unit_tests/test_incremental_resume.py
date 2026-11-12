#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


HISTORY_URL = "https://slack.com/api/conversations.history"
REPLIES_URL = "https://slack.com/api/conversations.replies"
LIST_URL = "https://slack.com/api/conversations.list"
ONE_DAY = 86400

MEMBER_CHANNEL = {"id": "C_MEMBER", "name": "member", "is_member": True, "is_archived": False}
JOINABLE_CHANNEL = {"id": "C_JOINABLE", "name": "joinable", "is_member": False, "is_archived": False}
ARCHIVED_CHANNEL = {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True}


def _catalog(stream_name):
    return ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream_name, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )


def _history_requests(requests_mock):
    return [r for r in requests_mock.request_history if r.url.startswith(HISTORY_URL)]


def _query(request):
    return {k: v[0] for k, v in parse_qs(urlparse(request.url).query).items()}


@freeze_time("2021-07-30T00:00:00Z")
def test_threads_second_read_resumes_parent_messages_from_each_channel_cursor(requests_mock, token_config):
    token_config["channel_filter"] = []
    token_config["end_date"] = None
    start_ts = 1626984000  # 2021-07-22T20:00:00Z (config start_date)
    channel_ts = {"airbyte-for-beginners": 1627430400, "good-reads": 1627516800}  # 2021-07-28, 2021-07-29
    for channel, ts in channel_ts.items():
        requests_mock.register_uri(
            "GET",
            f"{HISTORY_URL}?channel={channel}",
            json={"ok": True, "messages": [{"ts": f"{ts}.000100", "reply_count": 1}]},
        )
    requests_mock.register_uri("GET", REPLIES_URL, json={"ok": True, "messages": []})

    catalog = _catalog("threads")
    first_state = StateBuilder().build()
    first = read(get_source(token_config, "threads", first_state), config=token_config, catalog=catalog, state=first_state)
    assert not first.errors
    assert {_query(r)["channel"]: float(_query(r)["oldest"]) for r in _history_requests(requests_mock)} == {
        "airbyte-for-beginners": start_ts,
        "good-reads": start_ts,
    }

    requests_mock.reset_mock()
    emitted_state = first.most_recent_state.stream_state.__dict__
    second_state = StateBuilder().with_stream_state("threads", emitted_state).build()
    second = read(get_source(token_config, "threads", second_state), config=token_config, catalog=catalog, state=second_state)

    assert not second.errors
    # lookback_window=1 day is applied to each channel's own cursor, not to start_date
    assert {_query(r)["channel"]: float(_query(r)["oldest"]) for r in _history_requests(requests_mock)} == {
        "airbyte-for-beginners": channel_ts["airbyte-for-beginners"] + 0.0001 - ONE_DAY,
        "good-reads": channel_ts["good-reads"] + 0.0001 - ONE_DAY,
    }


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@freeze_time("2021-07-23T20:00:00Z")
def test_archived_non_member_channels_are_not_read_when_join_channels_enabled(requests_mock, token_config, stream_name):
    token_config["channel_filter"] = []
    token_config["include_archived_channels"] = True
    token_config["join_channels"] = True
    requests_mock.register_uri(
        "GET",
        f"{LIST_URL}?limit=999&types=public_channel&exclude_archived=false",
        json={"ok": True, "channels": [MEMBER_CHANNEL, JOINABLE_CHANNEL, ARCHIVED_CHANNEL]},
    )
    requests_mock.register_uri("POST", "https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.register_uri("GET", HISTORY_URL, json={"ok": True, "messages": [{"ts": "1627000000.000100", "reply_count": 1}]})
    requests_mock.register_uri("GET", REPLIES_URL, json={"ok": True, "messages": [{"ts": "1627000001.000100"}]})

    state = StateBuilder().build()
    output = read(get_source(token_config, stream_name, state), config=token_config, catalog=_catalog(stream_name), state=state)

    assert not output.errors
    assert sorted({_query(r)["channel"] for r in _history_requests(requests_mock)}) == ["C_JOINABLE", "C_MEMBER"]
    assert sorted({record.record.data["channel_id"] for record in output.records}) == ["C_JOINABLE", "C_MEMBER"]
