# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter

import pytest
import requests_mock
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
APPS = [{"id": "app-1"}, {"id": "app-2"}]


def _endpoint(stream_name: str, app_id: str) -> str:
    return BASE_URL if stream_name == "applications" else f"{BASE_URL}/{app_id}/{stream_name}"


def _records(prefix: str, day: str) -> list[dict]:
    return [
        {"id": f"{prefix}-nano", "modified_at": f"2026-10-{day}T09:41:55.568082659Z"},
        {"id": f"{prefix}-micro", "modified_at": f"2026-10-{day}T08:00:00.123456Z"},
        {"id": f"{prefix}-milli", "modified_at": f"2026-10-{day}T07:00:00.123Z"},
        {"id": f"{prefix}-second", "modified_at": f"2026-10-{day}T06:00:00Z"},
    ]


def _state(output: EntrypointOutput, stream_name: str) -> dict:
    latest = output.most_recent_state
    assert latest is not None
    state = latest.stream_state.__dict__
    if stream_name == "applications":
        return {"applications": state}
    assert state["use_global_cursor"] is False
    assert state["lookback_window"] == 0
    assert state["parent_state"] == {}
    return {entry["partition"]["app_id"]: entry["cursor"] for entry in state["states"]}


def _data(output: EntrypointOutput) -> dict[str, dict]:
    records = {}
    for message in output.records:
        assert message.record is not None
        records[message.record.data["id"]] = message.record.data
    return records


@freeze_time("2026-11-01T00:00:00Z")
@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("with_stalled_state", [False, True])
def test_incremental_state_advances_and_resumes_per_partition(stream_name: str, with_stalled_state: bool) -> None:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    partitions = {"applications": "14"} if stream_name == "applications" else {"app-1": "14", "app-2": "02"}
    page_size = 20 if stream_name == "applications" else 100
    response_key = "apps" if stream_name == "applications" else stream_name
    expected_first = {}
    expected_second = {}
    expected_states = {}
    expected_requests: Counter[str] = Counter()
    initial_state = None
    if with_stalled_state:
        cursor = {"modified_at": "2026-01-01T00:00:00.000000Z"}
        stalled_state: dict[str, object]
        if stream_name == "applications":
            stalled_state = {"modified_at": cursor["modified_at"]}
        else:
            stalled_state = {
                "use_global_cursor": False,
                "states": [{"partition": {"app_id": partition, "parent_slice": {}}, "cursor": cursor} for partition in partitions],
                "lookback_window": 0,
                "parent_state": {},
            }
        initial_state = StateBuilder().with_stream_state(stream_name, stalled_state).build()

    with requests_mock.Mocker() as mocker:
        if stream_name != "applications":
            mocker.get(f"{BASE_URL}?page=1&per_page=20", json={"apps": APPS}, complete_qs=True)
            expected_requests[f"{BASE_URL}?page=1&per_page=20"] = 2

        for partition, day in partitions.items():
            endpoint = _endpoint(stream_name, partition)
            first_page = [
                {"id": f"{partition}-old-{index}", "modified_at": f"2026-10-{day}T05:00:00.904417302Z"} for index in range(page_size - 3)
            ]
            optional_cursors = [
                {"id": f"{partition}-missing"},
                {"id": f"{partition}-null", "modified_at": None},
                {"id": f"{partition}-empty", "modified_at": ""},
            ]
            latest = _records(partition, day)
            expected_first.update({record["id"]: {**record, "modified_at": record["modified_at"][:26] + "Z"} for record in first_page})
            expected_first.update(
                {
                    f"{partition}-missing": {"id": f"{partition}-missing"},
                    f"{partition}-null": {"id": f"{partition}-null"},
                    f"{partition}-empty": {"id": f"{partition}-empty", "modified_at": ""},
                }
            )
            expected_first.update(
                {
                    latest[0]["id"]: {**latest[0], "modified_at": f"2026-10-{day}T09:41:55.568082Z"},
                    latest[1]["id"]: latest[1],
                    latest[2]["id"]: {**latest[2], "modified_at": f"2026-10-{day}T07:00:00.123000Z"},
                    latest[3]["id"]: {**latest[3], "modified_at": f"2026-10-{day}T06:00:00.000000Z"},
                }
            )
            newer = {"id": f"{partition}-new", "modified_at": f"2026-10-{day}T10:00:00.999999999Z"}
            tied = {"id": f"{partition}-same-microsecond", "modified_at": f"2026-10-{day}T09:41:55.568082999Z"}
            # These list endpoints re-read all rows; the fix must not introduce filtering or lose sub-microsecond ties.
            expected_second.update(expected_first)
            expected_second.update(
                {
                    tied["id"]: {**tied, "modified_at": f"2026-10-{day}T09:41:55.568082Z"},
                    newer["id"]: {**newer, "modified_at": f"2026-10-{day}T10:00:00.999999Z"},
                }
            )
            expected_states[partition] = {"modified_at": f"2026-10-{day}T09:41:55.568082Z"}
            first_url = f"{endpoint}?page=1&per_page={page_size}"
            second_url = f"{endpoint}?page=2&per_page={page_size}"
            mocker.get(first_url, json={response_key: first_page + optional_cursors}, complete_qs=True)
            mocker.get(
                second_url,
                [{"json": {response_key: latest}}, {"json": {response_key: latest + [tied, newer]}}],
                complete_qs=True,
            )
            expected_requests[first_url] = 2
            expected_requests[second_url] = 2

        first = read(get_source(CONFIG, state=initial_state), config=CONFIG, catalog=catalog, state=initial_state)
        assert first.errors == []
        assert _state(first, stream_name) == expected_states
        assert len(first.records) == len(expected_first)
        assert _data(first) == expected_first

        first_state = first.most_recent_state
        assert first_state is not None
        state = StateBuilder().with_stream_state(stream_name, first_state.stream_state).build()
        second = read(get_source(CONFIG, state=state), config=CONFIG, catalog=catalog, state=state)
        assert second.errors == []
        assert len(second.records) == len(expected_second)
        assert _data(second) == expected_second
        assert _state(second, stream_name) == {
            partition: {"modified_at": f"2026-10-{day}T10:00:00.999999Z"} for partition, day in partitions.items()
        }
        assert Counter(request.url for request in mocker.request_history) == expected_requests
