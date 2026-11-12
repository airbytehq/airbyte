# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
STREAMS = ["applications", "datasets", "models"]
OLD = "2026-10-02T17:05:11.904417Z"
NEW_RAW = "2026-10-14T09:41:55.568082659Z"
NEW = "2026-10-14T09:41:55.568082Z"
LATEST_RAW = "2026-10-15T09:41:55.568082999Z"
LATEST = "2026-10-15T09:41:55.568082Z"


def _read(stream_name: str, records: list[dict], state: list[AirbyteStateMessage] | None = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with requests_mock.Mocker() as mocker:
        if stream_name == "applications":
            endpoints = [(APPS_URL, "apps", 20)]
        else:
            mocker.get(
                f"{APPS_URL}?page=1&per_page=20",
                json={"apps": [{"id": app_id, "modified_at": NEW_RAW} for app_id in ("app1", "app2")]},
                complete_qs=True,
            )
            endpoints = [(f"{APPS_URL}/{app_id}/{stream_name}", stream_name, 100) for app_id in ("app1", "app2")]

        expected_requests = 0 if stream_name == "applications" else 1
        for url, response_key, page_size in endpoints:
            for page, offset in enumerate(range(0, len(records) + 1, page_size), start=1):
                mocker.get(
                    f"{url}?page={page}&per_page={page_size}",
                    json={response_key: records[offset : offset + page_size]},
                    complete_qs=True,
                )
                expected_requests += 1
        output = read(get_source(CONFIG, state=state), config=CONFIG, catalog=catalog, state=state)
        assert mocker.call_count == expected_requests
        assert all(request.headers["Authorization"] == "Bearer test_api_key" for request in mocker.request_history)
    assert not any("failed to parse cursor" in message.log.message for message in output.logs)
    return output


def _cursors(output: EntrypointOutput, stream_name: str) -> dict[str, str]:
    state = output.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        return {"applications": state["modified_at"]}
    return {partition["partition"]["app_id"]: partition["cursor"]["modified_at"] for partition in state["states"]}


def _assert_records(output: EntrypointOutput, stream_name: str, expected: list[dict]) -> None:
    copies = 1 if stream_name == "applications" else 2
    assert sorted((message.record.data for message in output.records), key=lambda record: record["id"]) == sorted(
        expected * copies, key=lambda record: record["id"]
    )


@pytest.mark.parametrize("stream_name", STREAMS)
def test_incremental_reads_checkpoint_and_resume(stream_name: str) -> None:
    page_size = 20 if stream_name == "applications" else 100
    records = [{"id": f"record-{index}", "modified_at": OLD} for index in range(page_size - 1)]
    # The boundary records share a microsecond but differ in nanoseconds, across pages.
    records.extend(
        [
            {"id": "boundary-first", "modified_at": "2026-10-14T09:41:55.568082001Z"},
            {"id": "boundary-second", "modified_at": NEW_RAW},
        ]
    )
    expected = records[:-2] + [
        {"id": "boundary-first", "modified_at": NEW},
        {"id": "boundary-second", "modified_at": NEW},
    ]
    first = _read(stream_name, records)
    _assert_records(first, stream_name, expected)
    partitions = ["applications"] if stream_name == "applications" else ["app1", "app2"]
    assert _cursors(first, stream_name) == dict.fromkeys(partitions, NEW)

    state = [message.state for message in first.state_messages[-1:]]
    second = _read(stream_name, records + [{"id": "updated", "modified_at": LATEST_RAW}], state)
    # These list endpoints still reread all records; this fix adds no date filter or early stopping.
    _assert_records(second, stream_name, expected + [{"id": "updated", "modified_at": LATEST}])
    assert _cursors(second, stream_name) == dict.fromkeys(partitions, LATEST)

    state = [message.state for message in second.state_messages[-1:]]
    empty = _read(stream_name, [], state)
    assert empty.records == []
    assert _cursors(empty, stream_name) == dict.fromkeys(partitions, LATEST)


@pytest.mark.parametrize(
    "stream_name,state_shape",
    [
        ("applications", "global"),
        ("datasets", "global"),
        ("models", "global"),
        ("datasets", "per_partition"),
        ("models", "per_partition"),
    ],
)
def test_saved_state_accepts_mixed_precision_timestamps(stream_name: str, state_shape: str) -> None:
    cursor = {"modified_at": "2026-01-01T00:00:00.000000Z"}
    saved = cursor
    if state_shape == "per_partition":
        saved = {
            "states": [{"partition": {"app_id": app_id, "parent_slice": {}}, "cursor": cursor} for app_id in ("app1", "app2")],
            "state": cursor,
            "use_global_cursor": False,
            "lookback_window": 0,
        }
    state = StateBuilder().with_stream_state(stream_name, saved).build()
    records = [
        {"id": "seconds", "modified_at": "2026-10-01T00:00:00Z"},
        {"id": "milliseconds", "modified_at": "2026-10-02T00:00:00.123Z"},
        {"id": "microseconds", "modified_at": OLD},
        {"id": "nanoseconds", "modified_at": NEW_RAW},
    ]
    output = _read(stream_name, records, state)
    _assert_records(
        output,
        stream_name,
        [
            {"id": "seconds", "modified_at": "2026-10-01T00:00:00.000000Z"},
            {"id": "milliseconds", "modified_at": "2026-10-02T00:00:00.123000Z"},
            {"id": "microseconds", "modified_at": OLD},
            {"id": "nanoseconds", "modified_at": NEW},
        ],
    )
    assert set(_cursors(output, stream_name).values()) == {NEW}
