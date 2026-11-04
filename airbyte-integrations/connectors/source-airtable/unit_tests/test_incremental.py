# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests_mock
import yaml
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"credentials": {"auth_method": "api_key", "api_key": "key"}}
_BASE_URL = "https://api.airtable.com/v0"
_STREAMS = {
    "base/table_a/tbl1": "tbl1",
    "base/table_b/tbl2": "tbl2",
}
_CURSOR_FIELD = "_airtable_extracted_at"
_SYNC_TIME = "2024-06-01T12:00:00Z"
_PRIOR_STATE = "2024-01-01T00:00:00Z"
_LOOKBACK_START = "2023-12-31T23:45:00Z"
# CREATED_TIME() must remain in IF(LAST_MODIFIED_TIME(), ...) for never-edited records.
_FILTER_FORMULA = f"IS_AFTER(IF(LAST_MODIFIED_TIME(), LAST_MODIFIED_TIME(), CREATED_TIME()), '{_LOOKBACK_START}')"


def _get_source(state=None):
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return ConcurrentDeclarativeSource(source_config=manifest, config=_CONFIG, catalog=None, state=state)


def _mock_api(mocker, empty_records=False):
    mocker.get(
        f"{_BASE_URL}/meta/bases",
        json={"bases": [{"id": "app1", "name": "base", "permissionLevel": "create"}]},
    )
    mocker.get(
        f"{_BASE_URL}/meta/bases/app1/tables",
        json={
            "tables": [
                {"id": "tbl1", "name": "Table A", "fields": [{"name": "Name", "type": "singleLineText"}]},
                {"id": "tbl2", "name": "Table B", "fields": [{"name": "Name", "type": "singleLineText"}]},
            ]
        },
    )

    if empty_records:
        mocker.get(f"{_BASE_URL}/app1/tbl1", json={"records": []})
        mocker.get(f"{_BASE_URL}/app1/tbl2", json={"records": []})
        return

    mocker.get(
        f"{_BASE_URL}/app1/tbl1",
        [
            {
                "json": {
                    "records": [
                        {"id": "rec1", "createdTime": "2024-05-01T00:00:00.000Z", "fields": {"Name": "one"}},
                        {"id": "empty", "createdTime": "2024-05-02T00:00:00.000Z", "fields": {}},
                    ],
                    "offset": "page2",
                }
            },
            {"json": {"records": [{"id": "rec2", "createdTime": "2024-05-03T00:00:00.000Z", "fields": {"Name": "two"}}]}},
        ],
    )
    mocker.get(
        f"{_BASE_URL}/app1/tbl2",
        json={"records": [{"id": "rec3", "createdTime": "2024-05-04T00:00:00.000Z", "fields": {"Name": "three"}}]},
    )


def _read(mode, state=None):
    builder = CatalogBuilder()
    for name in _STREAMS:
        builder.with_stream(name, mode)
    catalog = builder.build()
    return read(_get_source(state), _CONFIG, catalog, state)


def _records(output):
    return [message.record.data for message in output.records]


def _final_states(output):
    states = {}
    for message in output.state_messages:
        stream_state = message.state.stream
        states[stream_state.stream_descriptor.name] = stream_state.stream_state.__dict__
    return states


def _query_params(request):
    return parse_qs(urlparse(request.url).query)


def _assert_record_request_params(mocker, expected_by_table):
    actual_by_table = {table_id: [] for table_id in _STREAMS.values()}
    for request in mocker.request_history:
        for table_id in actual_by_table:
            if urlparse(request.url).path == f"/v0/app1/{table_id}":
                actual_by_table[table_id].append(_query_params(request))
    assert {table_id: queries for table_id, queries in actual_by_table.items()} == expected_by_table


def _expected_unfiltered_params():
    return {
        "tbl1": [{}, {"offset": ["page2"]}],
        "tbl2": [{}],
    }


def test_discover_exposes_incremental_cursor_and_full_refresh():
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        output = discover(_get_source(), _CONFIG)

    streams = {stream.name: stream for stream in output.catalog.catalog.streams}
    assert set(streams) == set(_STREAMS)
    for stream in streams.values():
        assert {mode.value for mode in stream.supported_sync_modes} == {"full_refresh", "incremental"}
        assert stream.default_cursor_field == [_CURSOR_FIELD]
        assert _CURSOR_FIELD in stream.json_schema["properties"]


@freeze_time("2024-06-01T12:00:00Z")
def test_full_refresh_does_not_filter_and_stamps_sync_window_end():
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        output = _read(SyncMode.full_refresh)

    _assert_record_request_params(mocker, _expected_unfiltered_params())
    records = _records(output)
    assert len(records) == 3
    assert all(record[_CURSOR_FIELD] == _SYNC_TIME for record in records)
    assert "empty" not in {record.get("_airtable_id") for record in records}


@freeze_time("2024-06-01T12:00:00Z")
def test_incremental_without_state_does_not_filter_and_advances_each_stream():
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        output = _read(SyncMode.incremental)

    _assert_record_request_params(mocker, _expected_unfiltered_params())
    assert _final_states(output) == {stream_name: {_CURSOR_FIELD: _SYNC_TIME} for stream_name in _STREAMS}


@freeze_time("2024-06-01T12:00:00Z")
def test_incremental_with_state_applies_lookback_and_advances_each_stream():
    state = (
        StateBuilder()
        .with_stream_state("base/table_a/tbl1", {_CURSOR_FIELD: _PRIOR_STATE})
        .with_stream_state("base/table_b/tbl2", {_CURSOR_FIELD: _PRIOR_STATE})
        .build()
    )
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker)
        output = _read(SyncMode.incremental, state)

    _assert_record_request_params(
        mocker,
        {
            "tbl1": [
                {"filterByFormula": [_FILTER_FORMULA]},
                {"filterByFormula": [_FILTER_FORMULA], "offset": ["page2"]},
            ],
            "tbl2": [{"filterByFormula": [_FILTER_FORMULA]}],
        },
    )
    assert _final_states(output) == {stream_name: {_CURSOR_FIELD: _SYNC_TIME} for stream_name in _STREAMS}


@freeze_time("2024-06-01T12:00:00Z")
def test_incremental_with_empty_api_responses_preserves_input_state():
    state = (
        StateBuilder()
        .with_stream_state("base/table_a/tbl1", {_CURSOR_FIELD: _PRIOR_STATE})
        .with_stream_state("base/table_b/tbl2", {_CURSOR_FIELD: _PRIOR_STATE})
        .build()
    )
    with requests_mock.Mocker() as mocker:
        _mock_api(mocker, empty_records=True)
        output = _read(SyncMode.incremental, state)

    assert _final_states(output) == {stream_name: {_CURSOR_FIELD: _PRIOR_STATE} for stream_name in _STREAMS}
