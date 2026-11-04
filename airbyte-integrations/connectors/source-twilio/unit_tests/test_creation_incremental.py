# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse

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
        requests_mock,
        CONVERSATIONS,
        "conversations",
        [{"sid": "CH1", "date_created": "Thu, 10 Nov 2022 12:00:00 +0000"}],
        StartDate=f"{start}T00:00:00Z",
        EndDate="2022-11-16T23:59:59Z",
    )
    state = state_for("conversations", {"date_created": "2022-11-10"}) if lookback is not None else None
    output = read_from_stream(
        {**TEST_CONFIG, "lookback_window": lookback or 0},
        "conversations",
        SyncMode.incremental if state else SyncMode.full_refresh,
        state,
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
        json={"conversations": []},
        status_code=status,
        complete_qs=True,
    )
    output = read_from_stream(TEST_CONFIG, "conversations", SyncMode.incremental)
    assert not output.records
    assert matcher.call_count == 1


@freeze_time(NOW)
@pytest.mark.parametrize("stream", ["executions", "step"])
@pytest.mark.parametrize("lookback", [0, 60])
def test_executions_partition_state(requests_mock, stream, lookback):
    register(requests_mock, FLOWS, "flows", [{"sid": "FW1"}, {"sid": "FW2"}])
    states = []
    matchers = []
    for flow, day, end_day in [("FW1", "01", "29"), ("FW2", "02", "30")]:
        cursor = f"2022-10-{day}T12:00:00Z"
        hour = "11" if lookback else "12"
        windows = [
            (f"2022-10-{day}T{hour}:00:00Z", f"2022-10-{end_day}T{hour}:00:00Z"),
            (f"2022-10-{end_day}T{hour}:00:00Z", NOW),
        ]
        states.append({"partition": {"sid": flow, "parent_slice": {}}, "cursor": {"date_created": cursor}})
        for index, (lower, next_lower) in enumerate(windows):
            upper = (
                (datetime.fromisoformat(next_lower.replace("Z", "+00:00")) - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                if index == 0
                else NOW
            )
            sid = f"FN{flow}{index}"
            matchers.append(
                register(
                    requests_mock,
                    f"{FLOWS}/{flow}/Executions",
                    "executions",
                    [{"sid": sid, "flow_sid": flow, "date_created": lower}],
                    DateCreatedFrom=lower,
                    DateCreatedTo=upper,
                )
            )
            if stream == "step":
                matchers.append(
                    register(
                        requests_mock,
                        f"{FLOWS}/{flow}/Executions/{sid}/Steps",
                        "steps",
                        [{"sid": f"FT{sid}", "date_created": lower}],
                    )
                )
    initial = {"states": states}
    if stream == "step":
        initial = {"state": {"date_created": "2022-10-01T00:00:00Z"}, "parent_state": {"executions": initial}}
    config = {**TEST_CONFIG, "lookback_window": lookback}
    output = read_from_stream(config, stream, SyncMode.incremental, state_for(stream, initial))
    assert len(output.records) == 4
    assert all(matcher.call_count == 1 for matcher in matchers)
    saved = final_state(output)
    parent = saved["parent_state"]["executions"] if stream == "step" else saved
    expected = {
        "FW1": {"date_created": f"2022-10-29T{'11' if lookback else '12'}:00:00Z"},
        "FW2": {"date_created": f"2022-10-30T{'11' if lookback else '12'}:00:00Z"},
    }
    assert {s["partition"]["sid"]: s["cursor"] for s in parent["states"]} == expected
    if stream == "step":
        resumed_matchers = []
        for flow, cursor in expected.items():
            lower = datetime.fromisoformat(cursor["date_created"].replace("Z", "+00:00")) - timedelta(minutes=lookback)
            lower = lower.strftime("%Y-%m-%dT%H:%M:%SZ")
            resumed_matchers.append(
                register(
                    requests_mock,
                    f"{FLOWS}/{flow}/Executions",
                    "executions",
                    [{"sid": f"FN{flow}1", "flow_sid": flow, "date_created": lower}],
                    DateCreatedFrom=lower,
                    DateCreatedTo=NOW,
                )
            )
        resumed = read_from_stream(config, stream, SyncMode.incremental, state_for(stream, saved))
        assert len(resumed.records) == 2
        assert all(matcher.call_count == 1 for matcher in resumed_matchers)
        assert "executions" in final_state(resumed)["parent_state"]


@freeze_time(NOW)
def test_executions_cold_full_refresh_window_bound(requests_mock):
    register(requests_mock, FLOWS, "flows", [{"sid": "FW1"}, {"sid": "FW2"}])
    windows = {"FW1": [], "FW2": []}

    def executions_response(request, context):
        query = parse_qs(urlparse(request.url).query)
        assert set(query) == {"PageSize", "DateCreatedFrom", "DateCreatedTo"}
        assert query["PageSize"] == ["1000"]
        lower = datetime.fromisoformat(query["DateCreatedFrom"][0].replace("Z", "+00:00"))
        upper = datetime.fromisoformat(query["DateCreatedTo"][0].replace("Z", "+00:00"))
        flow = urlparse(request.url).path.split("/")[3]
        windows[flow].append((lower, upper))
        return {"executions": []}

    for flow in windows:
        requests_mock.get(f"{FLOWS}/{flow}/Executions", json=executions_response)
    output = read_from_stream(TEST_CONFIG, "executions", SyncMode.full_refresh)
    assert not output.records
    for slices in windows.values():
        slices.sort()
        assert all(timedelta(0) <= upper - lower <= timedelta(days=28) for lower, upper in slices)
        assert len(slices) > 1
        assert slices[0][0] == datetime.fromisoformat("2010-01-01T00:00:00+00:00")
        assert slices[-1][1] == datetime.fromisoformat(NOW.replace("Z", "+00:00"))
        assert all(left[1] + timedelta(seconds=1) == right[0] for left, right in zip(slices, slices[1:]))
