# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


HISTORY_URL = "https://slack.com/api/conversations.history"
REPLIES_URL = "https://slack.com/api/conversations.replies"
LIST_URL = "https://slack.com/api/conversations.list"

# lookback_window in base_config is 1 day
ONE_DAY = 86400
CHANNEL_A_CURSOR = 1627776000.0  # 2021-08-01T00:00:00Z
CHANNEL_B_CURSOR = 1628985600.0  # 2021-08-15T00:00:00Z
START_DATE_TS = 1626984000.0  # 2021-07-22T20:00:00Z


def _catalog(stream_name: str):
    return CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name)).build()


def _history_requests(requests_mock):
    return [r for r in requests_mock.request_history if r.url.startswith(HISTORY_URL)]


def _oldest_by_channel(requests_mock):
    result = {}
    for request in _history_requests(requests_mock):
        query = parse_qs(urlparse(request.url).query)
        result.setdefault(query["channel"][0], []).append(float(query["oldest"][0]))
    return result


def _checkpointed_threads_state():
    """Threads state as emitted by the connector after a partially completed attempt: per-channel
    channel_messages cursors are stored under parent_state, no thread partition completed yet."""
    return {
        "use_global_cursor": False,
        "states": [],
        "state": {"float_ts": str(int(START_DATE_TS))},
        "lookback_window": 0,
        "parent_state": {
            "channel_messages": {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"channel": "airbyte-for-beginners", "parent_slice": {}}, "cursor": {"float_ts": str(CHANNEL_A_CURSOR)}},
                    {"partition": {"channel": "good-reads", "parent_slice": {}}, "cursor": {"float_ts": str(CHANNEL_B_CURSOR)}},
                ],
                "state": {"float_ts": str(CHANNEL_A_CURSOR)},
                "lookback_window": ONE_DAY,
                "parent_state": {},
            }
        },
    }


def test_threads_resumes_parent_channel_messages_from_per_channel_cursors(requests_mock, token_config):
    requests_mock.register_uri("GET", HISTORY_URL, json={"ok": True, "messages": []})
    requests_mock.register_uri("GET", REPLIES_URL, json={"ok": True, "messages": []})
    state = StateBuilder().with_stream_state("threads", _checkpointed_threads_state()).build()

    output = read(get_source(token_config, "threads", state), token_config, _catalog("threads"), state)

    assert not output.errors
    oldest = _oldest_by_channel(requests_mock)
    # Each channel resumes from its own checkpoint (minus the 1-day lookback), not from start_date
    assert min(oldest["airbyte-for-beginners"]) == CHANNEL_A_CURSOR - ONE_DAY
    assert min(oldest["good-reads"]) == CHANNEL_B_CURSOR - ONE_DAY
    # the per-channel parent cursors are still present in the emitted state
    final_parent_state = output.most_recent_state.stream_state.__dict__["parent_state"]["channel_messages"]
    channels_in_state = {s["partition"]["channel"] for s in final_parent_state["states"]}
    assert channels_in_state == {"airbyte-for-beginners", "good-reads"}


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_non_member_channels_are_not_partitioned_when_joining(requests_mock, token_config, stream_name):
    token_config["channel_filter"] = []
    token_config["include_archived_channels"] = True
    token_config["join_channels"] = True
    channels = [
        {"id": "C_MEMBER", "name": "member", "is_member": True, "is_archived": False},
        {"id": "C_JOINABLE", "name": "joinable", "is_member": False, "is_archived": False},
        {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
        {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
    ]
    requests_mock.register_uri(
        "GET", f"{LIST_URL}?limit=999&types=public_channel&exclude_archived=false", json={"ok": True, "channels": channels}
    )
    requests_mock.register_uri("POST", "https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.register_uri("GET", HISTORY_URL, json={"ok": True, "messages": []})
    requests_mock.register_uri("GET", REPLIES_URL, json={"ok": True, "messages": []})

    output = read(get_source(token_config, stream_name), token_config, _catalog(stream_name))

    assert not output.errors
    assert set(_oldest_by_channel(requests_mock)) == {"C_MEMBER", "C_JOINABLE", "C_ARCHIVED_MEMBER"}
    joined = [r.json()["channel"] for r in requests_mock.request_history if r.url.endswith("conversations.join")]
    assert joined == ["C_JOINABLE"]
