# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from urllib.parse import urlencode

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time
from test_streams import read_from_stream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


CONVERSATIONS = "https://conversations.twilio.com/v1/Conversations"
FLOWS = "https://studio.twilio.com/v1/Flows"
NOW = "2022-11-16T12:03:11Z"


def register(requests_mock, url: str, field: str, records: list, **params):
    return requests_mock.get(f"{url}?{urlencode({'PageSize': 1000, **params})}", json={field: records}, complete_qs=True)


def state_for(name: str, value: dict):
    return StateBuilder().with_stream_state(name, value).build()


def final_state(output):
    return output.most_recent_state.stream_state.__dict__


@pytest.mark.parametrize("name", ["conversations", "executions", "step"])
def test_discover_incremental(name):
    streams = get_source(TEST_CONFIG).discover(logging.getLogger("test"), TEST_CONFIG).streams
    stream = next(stream for stream in streams if stream.name == name)
    assert set(stream.supported_sync_modes) == {SyncMode.full_refresh, SyncMode.incremental}
    assert stream.default_cursor_field == ["date_created"]


@freeze_time(NOW)
@pytest.mark.parametrize("lookback,start", [(None, "2010-01-01"), (0, "2022-11-10"), (60, "2022-11-09")])
def test_conversations(requests_mock, lookback, start):
    matcher = register(
        requests_mock, CONVERSATIONS, "conversations",
        [{"sid": "CH1", "date_created": "Thu, 10 Nov 2022 12:00:00 +0000"}],
        StartDate=f"{start}T00:00:00Z", EndDate="2022-11-16T23:59:59Z",
    )
    state = state_for("conversations", {"date_created": "2022-11-10"}) if lookback is not None else None
    output = read_from_stream(
        {**TEST_CONFIG, "lookback_window": lookback or 0}, "conversations",
        SyncMode.incremental if state else SyncMode.full_refresh, state,
    )
    assert matcher.call_count == 1
    assert len(output.records) == 1
    if state:
        assert final_state(output) == {"date_created": "2022-11-10"}
    if lookback == 0:
        resumed = read_from_stream(TEST_CONFIG, "conversations", SyncMode.incremental, state_for("conversations", final_state(output)))
        assert final_state(resumed) == {"date_created": "2022-11-10"}
        assert matcher.call_count == 2


@freeze_time(NOW)
def test_conversation_children_keep_full_parent(requests_mock):
    parent = register(requests_mock, CONVERSATIONS, "conversations", [{"sid": "CH1"}])
    child = register(requests_mock, f"{CONVERSATIONS}/CH1/Messages", "messages", [{"sid": "IM1"}])
    assert len(read_from_stream(TEST_CONFIG, "conversation_messages", SyncMode.full_refresh).records) == 1
    assert parent.call_count == child.call_count == 1


@freeze_time(NOW)
@pytest.mark.parametrize("status", [200, 404])
def test_conversations_empty_or_missing(requests_mock, status):
    matcher = requests_mock.get(
        f"{CONVERSATIONS}?{urlencode({'PageSize': 1000, 'StartDate': '2010-01-01T00:00:00Z', 'EndDate': '2022-11-16T23:59:59Z'})}",
        json={"conversations": []}, status_code=status, complete_qs=True,
    )
    output = read_from_stream(TEST_CONFIG, "conversations", SyncMode.incremental)
    assert not output.records
    assert matcher.call_count == 1


@freeze_time(NOW)
def test_executions_partition_state(requests_mock):
    register(requests_mock, FLOWS, "flows", [{"sid": "FW1"}, {"sid": "FW2"}])
    states = []
    matchers = []
    for flow, day in [("FW1", "10"), ("FW2", "11")]:
        cursor = f"2022-11-{day}T12:00:00Z"
        states.append({"partition": {"sid": flow, "parent_slice": {}}, "cursor": {"date_created": cursor}})
        matchers.append(register(
            requests_mock, f"{FLOWS}/{flow}/Executions", "executions",
            [{"sid": f"FN{day}", "flow_sid": flow, "date_created": "2022-11-15T12:00:00Z"}],
            DateCreatedFrom=cursor, DateCreatedTo=NOW,
        ))
    output = read_from_stream(TEST_CONFIG, "executions", SyncMode.incremental, state_for("executions", {"states": states}))
    assert len(output.records) == 2
    assert all(matcher.call_count == 1 for matcher in matchers)
    assert {s["partition"]["sid"]: s["cursor"] for s in final_state(output)["states"]} == {
        flow: {"date_created": "2022-11-15T12:00:00Z"} for flow in ["FW1", "FW2"]
    }


@freeze_time(NOW)
def test_step_nested_parent_state(requests_mock):
    register(requests_mock, FLOWS, "flows", [{"sid": "FW1"}])
    first = register(
        requests_mock, f"{FLOWS}/FW1/Executions", "executions",
        [{"sid": "FN1", "flow_sid": "FW1", "date_created": "2022-11-15T12:00:00Z"}],
        DateCreatedFrom="2010-01-01T00:00:00Z", DateCreatedTo=NOW,
    )
    child = register(
        requests_mock, f"{FLOWS}/FW1/Executions/FN1/Steps", "steps",
        [{"sid": "FT1", "date_created": "2022-11-15T12:01:00Z"}],
    )
    output = read_from_stream(TEST_CONFIG, "step", SyncMode.incremental)
    saved = final_state(output)
    assert saved["parent_state"]["executions"]["states"][0]["cursor"] == {"date_created": "2022-11-15T12:00:00Z"}
    second = register(
        requests_mock, f"{FLOWS}/FW1/Executions", "executions",
        [{"sid": "FN1", "flow_sid": "FW1", "date_created": "2022-11-15T12:00:00Z"}],
        DateCreatedFrom="2022-11-15T12:00:00Z", DateCreatedTo=NOW,
    )
    resumed = read_from_stream(TEST_CONFIG, "step", SyncMode.incremental, state_for("step", saved))
    assert len(output.records) == len(resumed.records) == 1
    assert first.call_count == second.call_count == 1
    assert child.call_count == 2
