# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Mapping

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2026-01-01T00:00:00Z",
}
_START_CURSOR = "2026-01-01T00:00:00.000000Z"
_APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
_APP_IDS = ("app1", "app2")
_STREAM_NAMES = ("applications", "datasets", "models")


def _initial_state(stream_name: str) -> list[AirbyteStateMessage]:
    state: dict[str, object]
    if stream_name == "applications":
        state = {"modified_at": _START_CURSOR}
    else:
        state = {"states": [{"partition": {"app_id": app_id}, "cursor": {"modified_at": _START_CURSOR}} for app_id in _APP_IDS]}
    return StateBuilder().with_stream_state(stream_name, state).build()


def _read_stream(
    stream_name: str,
    records: list[dict[str, str]],
    state: list[AirbyteStateMessage],
    records_by_app: Mapping[str, list[dict[str, str]]] | None = None,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with requests_mock.Mocker() as mocker:
        if stream_name == "applications":
            mocker.get(f"{_APPS_URL}?page=1&per_page=20", json={"apps": records}, complete_qs=True)
        else:
            mocker.get(
                f"{_APPS_URL}?page=1&per_page=20",
                json={"apps": [{"id": app_id, "modified_at": "2026-10-01T00:00:00.123456789Z"} for app_id in _APP_IDS]},
                complete_qs=True,
            )
            for app_id in _APP_IDS:
                mocker.get(
                    f"{_APPS_URL}/{app_id}/{stream_name}?page=1&per_page=100",
                    json={stream_name: records_by_app[app_id] if records_by_app is not None else records},
                    complete_qs=True,
                )
        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)
    assert not output.errors
    return output


def _assert_cursors(output: EntrypointOutput, stream_name: str, expected: Mapping[str, str]) -> None:
    state = output.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        assert state == expected
    else:
        assert {partition["partition"]["app_id"]: partition["cursor"] for partition in state["states"]} == {
            app_id: expected for app_id in _APP_IDS
        }


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
@pytest.mark.parametrize(
    "timestamp,expected_cursor",
    [
        ("2026-10-14T09:41:55.568082659Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568082Z", "2026-10-14T09:41:55.568082Z"),
        ("2026-10-14T09:41:55.568Z", "2026-10-14T09:41:55.568000Z"),
        ("2026-10-14T09:41:55Z", "2026-10-14T09:41:55.000000Z"),
    ],
)
def test_incremental_state_advances(stream_name: str, timestamp: str, expected_cursor: str) -> None:
    records = [
        {"id": "newest", "modified_at": timestamp},
        {"id": "older", "modified_at": "2026-10-02T17:05:11.904417302Z"},
    ]
    output = _read_stream(stream_name, records, _initial_state(stream_name))

    assert len(output.records) == len(records) * (1 if stream_name == "applications" else len(_APP_IDS))
    assert {message.record.data["modified_at"] for message in output.records} == {
        expected_cursor,
        "2026-10-02T17:05:11.904417Z",
    }
    _assert_cursors(output, stream_name, {"modified_at": expected_cursor})
    assert not output.is_in_logs("Could not find cursor field")


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_incremental_state_survives_resume_and_empty_sync(stream_name: str) -> None:
    first = _read_stream(
        stream_name,
        [{"id": "first", "modified_at": "2026-10-02T17:05:11.904417302Z"}],
        _initial_state(stream_name),
    )
    _assert_cursors(first, stream_name, {"modified_at": "2026-10-02T17:05:11.904417Z"})

    resumed = _read_stream(
        stream_name,
        [
            {"id": "older", "modified_at": "2026-09-01T00:00:00Z"},
            {"id": "newer", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        ],
        [first.state_messages[-1].state],
    )
    _assert_cursors(resumed, stream_name, {"modified_at": "2026-10-14T09:41:55.568082Z"})

    empty = _read_stream(stream_name, [], [resumed.state_messages[-1].state])
    _assert_cursors(empty, stream_name, {"modified_at": "2026-10-14T09:41:55.568082Z"})


@pytest.mark.parametrize("stream_name", ["datasets", "models"])
def test_substream_cursors_advance_independently(stream_name: str) -> None:
    output = _read_stream(
        stream_name,
        [],
        _initial_state(stream_name),
        records_by_app={
            "app1": [{"id": "first", "modified_at": "2026-10-02T17:05:11.904417302Z"}],
            "app2": [{"id": "second", "modified_at": "2026-10-14T09:41:55.568082659Z"}],
        },
    )

    assert len(output.records) == 2
    assert {
        partition["partition"]["app_id"]: partition["cursor"]["modified_at"]
        for partition in output.most_recent_state.stream_state.__dict__["states"]
    } == {
        "app1": "2026-10-02T17:05:11.904417Z",
        "app2": "2026-10-14T09:41:55.568082Z",
    }
