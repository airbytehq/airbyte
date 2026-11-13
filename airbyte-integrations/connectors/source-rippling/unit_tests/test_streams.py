# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_BASE = "https://rest.ripplingapis.com"
_TOKEN = "rippling-test-token"
_HEADERS = {"Authorization": f"Bearer {_TOKEN}", "Rippling-Api-Version": "2024-08-01", "Accept": "application/json"}
_EPOCH = "1970-01-01T00:00:00"

# stream -> cursor field, for streams that sync incrementally with the server-side `filter` parameter.
INCREMENTAL_STREAMS = {
    "workers": "updated_at",
    "time_entries": "updated_at",
    "worker_time_splits": "updated_at",
    "app_users": "updated_at",
    "compensation_bands_details": "updated_at",
    "worker_changes": "applied_on",
    "activity_log": "occurred_at",
}


def _manifest() -> Mapping[str, Any]:
    with _MANIFEST_PATH.open() as manifest_file:
        return yaml.safe_load(manifest_file)


_STREAM_DEFS: Dict[str, Mapping[str, Any]] = _manifest()["definitions"]["streams"]
# custom_object_records is a substream of custom_objects and is covered by its own test.
TOP_LEVEL_STREAMS = {name: s["retriever"]["requester"]["path"] for name, s in _STREAM_DEFS.items() if name != "custom_object_records"}


def _config(**overrides: Any) -> Dict[str, Any]:
    return {"api_token": _TOKEN, **overrides}


def _read(config: Mapping[str, Any], stream: str, mode: SyncMode = SyncMode.full_refresh, state: Optional[List[Any]] = None):
    catalog: ConfiguredAirbyteCatalog = CatalogBuilder().with_stream(stream, mode).build()
    state = state if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _check(config: Mapping[str, Any]):
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), config=config)
    return source.check(logging.getLogger("airbyte"), config)


def _filter_query(stream: str, since: str = _EPOCH) -> Dict[str, str]:
    cursor = INCREMENTAL_STREAMS.get(stream)
    if not cursor:
        return {}
    return {"filter": f"{cursor} ge {since}", "order_by": f"{cursor} asc"}


def _request(path: str, headers: Optional[Mapping[str, str]] = None, **query: Any) -> HttpRequest:
    return HttpRequest(f"{_BASE}{path}", query_params=query or None, headers=headers or _HEADERS)


def _page(records: List[Mapping[str, Any]], next_link: Optional[str] = None) -> HttpResponse:
    return HttpResponse(json.dumps({"results": records, "next_link": next_link}))


def _record(stream: str, n: int, **extra: Any) -> Dict[str, Any]:
    key = "field_key" if stream == "worker_change_fields" else "id"
    record = {key: f"{stream}-{n}", **extra}
    cursor = INCREMENTAL_STREAMS.get(stream)
    if cursor:
        record.setdefault(cursor, f"2026-01-0{n}T00:00:00.000000+00:00")
    return record


def test_check_lists_companies() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/companies/", limit="100"), _page([{"id": "co-1", "name": "Acme"}]))
        status = _check(_config())

    assert status.status.value == "SUCCEEDED"


def test_check_reports_rejected_token_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/companies/", limit="100"), HttpResponse(json.dumps({"code": "UNAUTHORIZED"}), 401))
        status = _check(_config())

    assert status.status.value == "FAILED"
    assert "Rippling rejected the API token" in status.message


def test_missing_scope_fails_with_actionable_message() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/devices/", limit="100"), HttpResponse(json.dumps({"code": "FORBIDDEN"}), 403))
        output = _read(_config(), "devices")

    assert output.records == []
    messages = " ".join(str(e.trace.error.message) for e in output.errors)
    assert "missing the scope for this stream" in messages


@pytest.mark.parametrize("stream", sorted(TOP_LEVEL_STREAMS))
def test_stream_follows_next_link_until_it_is_null(stream: str) -> None:
    path = TOP_LEVEL_STREAMS[stream]
    # activity_log is clamped to its 90-day retention window: 2026-01-10 minus 89 days.
    query = _filter_query(stream, "2025-10-13T00:00:00" if stream == "activity_log" else _EPOCH)
    # Rippling returns next_link as an absolute URL that only carries the cursor. Like the official SDK,
    # the connector keeps sending limit, filter and order_by alongside it.
    next_link = f"{_BASE}{path}?cursor=cD0y"
    with HttpMocker() as http_mocker:
        http_mocker.get(_request(path, limit="100", **query), _page([_record(stream, 1), _record(stream, 2)], next_link))
        http_mocker.get(_request(path, limit="100", cursor="cD0y", **query), _page([_record(stream, 3)]))
        with freeze_time("2026-01-10T00:00:00Z"):
            output = _read(_config(), stream)

    key = "field_key" if stream == "worker_change_fields" else "id"
    assert [r.record.data[key] for r in output.records] == [f"{stream}-1", f"{stream}-2", f"{stream}-3"]
    assert not output.errors


def test_first_incremental_sync_reads_full_history_and_saves_max_cursor() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/workers/", limit="100", **_filter_query("workers")),
            _page(
                [
                    {"id": "w-1", "updated_at": "2025-11-02T08:00:00+00:00"},
                    {"id": "w-2", "updated_at": "2026-03-04T09:30:00.123000+00:00"},
                ]
            ),
        )
        with freeze_time("2026-03-06T00:00:00Z"):
            output = _read(_config(), "workers", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["w-1", "w-2"]
    assert output.most_recent_state.stream_state.__dict__["updated_at"] == "2026-03-04T09:30:00Z"


def test_start_date_becomes_server_side_filter() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/time-entries/", limit="100", **_filter_query("time_entries", "2025-06-01T00:00:00")),
            _page([{"id": "te-1", "updated_at": "2025-07-01T00:00:00+00:00"}]),
        )
        with freeze_time("2026-01-01T00:00:00Z"):
            output = _read(_config(start_date="2025-06-01T00:00:00Z"), "time_entries", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["te-1"]


def test_subsequent_sync_resumes_from_state() -> None:
    state = StateBuilder().with_stream_state("worker_changes", {"applied_on": "2026-02-01T12:30:45Z"}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/worker-changes/", limit="100", **_filter_query("worker_changes", "2026-02-01T12:30:45")),
            _page([{"id": "chg-9", "applied_on": "2026-02-03T00:00:00.000Z"}]),
        )
        with freeze_time("2026-02-04T00:00:00Z"):
            output = _read(_config(start_date="2020-01-01T00:00:00Z"), "worker_changes", SyncMode.incremental, state=state)

    assert [r.record.data["id"] for r in output.records] == ["chg-9"]
    assert output.most_recent_state.stream_state.__dict__["applied_on"] == "2026-02-03T00:00:00Z"


def test_activity_log_never_requests_events_older_than_retention() -> None:
    # Rippling keeps 90 days of activity log events; an old start date is clamped to now - 89 days.
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/activity-log/", limit="100", **_filter_query("activity_log", "2026-01-02T00:00:00")),
            _page([{"id": "ev-1", "occurred_at": "2026-03-01T10:00:00+00:00"}]),
        )
        with freeze_time("2026-04-01T00:00:00Z"):
            output = _read(_config(start_date="2020-01-01T00:00:00Z"), "activity_log", SyncMode.incremental)

    assert [r.record.data["id"] for r in output.records] == ["ev-1"]


def test_custom_object_records_are_read_per_custom_object() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/custom-objects/", limit="100"),
            _page([{"id": "obj-1", "api_name": "vehicle__c"}, {"id": "obj-2", "api_name": "badge__c"}]),
        )
        http_mocker.get(_request("/custom-objects/vehicle__c/records/", limit="100"), _page([{"id": "rec-1", "name": "Van"}]))
        http_mocker.get(_request("/custom-objects/badge__c/records/", limit="100"), _page([{"id": "rec-1", "name": "Blue"}]))
        output = _read(_config(), "custom_object_records")

    rows = sorted((r.record.data["custom_object_api_name"], r.record.data["id"]) for r in output.records)
    assert rows == [("badge__c", "rec-1"), ("vehicle__c", "rec-1")]
    assert _STREAM_DEFS["custom_object_records"]["primary_key"] == ["custom_object_api_name", "id"]


def test_rate_limited_request_is_retried(mocker) -> None:
    mocker.patch("time.sleep", lambda _: None)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _request("/departments/", limit="100"),
            [
                HttpResponse(json.dumps({"code": "RATE_LIMITED"}), 429, {"Retry-After": "1"}),
                _page([{"id": "dep-1", "name": "Engineering"}]),
            ],
        )
        output = _read(_config(), "departments")

    assert [r.record.data["id"] for r in output.records] == ["dep-1"]
    assert not output.errors


def test_api_version_can_be_overridden() -> None:
    headers = {**_HEADERS, "Rippling-Api-Version": "2025-01-01"}
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/teams/", headers=headers, limit="100"), _page([{"id": "team-1"}]))
        output = _read(_config(api_version="2025-01-01"), "teams")

    assert [r.record.data["id"] for r in output.records] == ["team-1"]


def test_incremental_streams_use_a_filterable_cursor_typed_as_date_time() -> None:
    for name, cursor in INCREMENTAL_STREAMS.items():
        stream = _STREAM_DEFS[name]
        assert stream["incremental_sync"]["$ref"] == f"#/definitions/{cursor}_cursor", name
        assert stream["schema_loader"]["schema"]["properties"][cursor]["format"] == "date-time", name
        assert stream["retriever"]["requester"]["request_parameters"]["order_by"] == f"{cursor} asc", name
    incremental = {name for name, s in _STREAM_DEFS.items() if "incremental_sync" in s}
    assert incremental == set(INCREMENTAL_STREAMS)


def test_every_stream_declares_its_primary_key_in_the_schema() -> None:
    for name, stream in _STREAM_DEFS.items():
        props = stream["schema_loader"]["schema"]["properties"]
        for key in stream["primary_key"]:
            assert key in props, (name, key)
