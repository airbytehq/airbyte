# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
_APPS = [{"id": app_id, "modified_at": "2026-01-02T00:00:00Z"} for app_id in ("app1", "app2")]


def _request(url: str, page_size: int, page: int) -> HttpRequest:
    return HttpRequest(url, query_params={"per_page": str(page_size), "page": str(page)}, headers={"Authorization": "Bearer test_api_key"})


def _response(key: str, records: list[dict]) -> HttpResponse:
    return HttpResponse(json.dumps({key: records}))


def _read(stream_name: str, records: dict[str, list[dict]], state: list[AirbyteStateMessage] | None = None) -> EntrypointOutput:
    page_size = 20 if stream_name == "applications" else 100
    with HttpMocker() as mocker:
        requests = []
        if stream_name != "applications":
            parent_request = _request(_BASE_URL, 20, 1)
            mocker.get(parent_request, _response("apps", _APPS))
            requests.append(parent_request)
        for partition, partition_records in records.items():
            url = _BASE_URL if stream_name == "applications" else f"{_BASE_URL}/{partition}/{stream_name}"
            key = "apps" if stream_name == "applications" else stream_name
            for offset in range(0, len(partition_records) + 1, page_size):
                request = _request(url, page_size, offset // page_size + 1)
                mocker.get(
                    request,
                    _response(key, partition_records[offset : offset + page_size]),
                )
                requests.append(request)
        output = read(
            get_source(_CONFIG, state=state),
            config=_CONFIG,
            catalog=CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build(),
            state=state,
        )
        for request in requests:
            mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    return output


def _assert_state(output: EntrypointOutput, stream_name: str, cursors: dict[str, str]) -> None:
    state = output.most_recent_state.stream_state.__dict__
    if stream_name == "applications":
        assert state == {"modified_at": cursors["applications"]}
    else:
        assert sorted(state["states"], key=lambda item: item["partition"]["app_id"]) == [
            {"partition": {"app_id": app_id, "parent_slice": {}}, "cursor": {"modified_at": cursor}} for app_id, cursor in cursors.items()
        ]
        assert state["use_global_cursor"] is False
        assert state["parent_state"] == {}


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize(
    "fraction,normalized_fraction",
    [("904417302", "904417"), ("904417", "904417"), ("904", "904000"), ("", "000000")],
    ids=["nanoseconds", "microseconds", "milliseconds", "seconds"],
)
def test_incremental_state_advances_and_resumes(stream_name: str, fraction: str, normalized_fraction: str) -> None:
    partitions = ["applications"] if stream_name == "applications" else ["app1", "app2"]
    page_size = 20 if stream_name == "applications" else 100
    suffix = f".{fraction}Z" if fraction else "Z"
    records = {}
    cursors = {}
    for index, partition in enumerate(partitions):
        day = 14 + index
        newest = f"2026-10-{day}T09:41:55{suffix}"
        # The newest record is not last, so checkpointing must track the maximum across pages.
        records[partition] = [{"id": f"{partition}-newest", "modified_at": newest}] + [
            {"id": f"{partition}-{record_id}", "modified_at": f"2026-10-02T17:05:11{suffix}"} for record_id in range(page_size)
        ]
        records[partition].extend(
            [
                {"id": f"{partition}-missing"},
                {"id": f"{partition}-null", "modified_at": None},
                {"id": f"{partition}-empty", "modified_at": ""},
            ]
        )
        cursors[partition] = f"2026-10-{day}T09:41:55.{normalized_fraction}Z"

    first = _read(stream_name, records)
    _assert_state(first, stream_name, cursors)
    expected = []
    for partition, partition_records in records.items():
        for record in partition_records:
            normalized = {key: value for key, value in record.items() if value is not None}
            if record.get("modified_at"):
                normalized["modified_at"] = (
                    cursors[partition] if record["id"].endswith("-newest") else f"2026-10-02T17:05:11.{normalized_fraction}Z"
                )
            expected.append(normalized)
    assert sorted((record.record.data for record in first.records), key=lambda record: record["id"]) == sorted(
        expected, key=lambda record: record["id"]
    )

    state = [first.state_messages[-1].state]
    for index, partition in enumerate(partitions):
        records[partition][1]["modified_at"] = f"2026-10-{20 + index}T17:05:11{suffix}"
        cursors[partition] = f"2026-10-{20 + index}T17:05:11.{normalized_fraction}Z"
        next(record for record in expected if record["id"] == records[partition][1]["id"])["modified_at"] = cursors[partition]
    resumed = _read(stream_name, records, state)
    _assert_state(resumed, stream_name, cursors)
    # These list endpoints have no configured date filter; preserve their full-scan replay contract.
    assert sorted((record.record.data for record in resumed.records), key=lambda record: record["id"]) == sorted(
        expected, key=lambda record: record["id"]
    )

    empty = _read(stream_name, {partition: [] for partition in partitions}, [resumed.state_messages[-1].state])
    assert empty.records == []
    _assert_state(empty, stream_name, cursors)
