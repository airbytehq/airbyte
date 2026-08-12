# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `reports-people` and `reports-projects` streams on `source-float`.

These streams read the Float Reports API (`GET /reports/people`, `GET /reports/projects`),
which differs from the other Float endpoints in three ways covered here:

* records are nested under a root key (`people` / `projects`) and unwrapped by a `DpathExtractor`,
* the date range is passed as `start_date` / `end_date` query params, derived from the config
  (`start_date` trimmed to `YYYY-MM-DD`, `end_date` defaulting to today via `now_utc()`),
* the endpoints do not support pagination, so the streams use `NoPagination`.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"

_BASE_URL = "https://api.float.com/v3"

_CONFIG = {
    "access_token": "test_access_token",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31",
}

# Config without the optional `end_date`, to exercise the `now_utc()` fallback.
_CONFIG_NO_END_DATE = {
    "access_token": "test_access_token",
    "start_date": "2024-01-01T00:00:00Z",
}

_EXISTING_STREAMS = [
    "accounts",
    "clients",
    "departments",
    "holidays",
    "logged-time",
    "milestones",
    "people",
    "phases",
    "project-tasks",
    "projects",
    "public_holidays",
    "roles",
    "status",
    "tasks",
    "time_off",
    "timeoff-types",
]

_REPORT_STREAMS = [
    pytest.param("reports-people", "/reports/people", "people", id="reports-people"),
    pytest.param("reports-projects", "/reports/projects", "projects", id="reports-projects"),
]


def _get_source(config=None):
    config = config or _CONFIG
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )


def _sync(stream_name, config=None):
    config = config or _CONFIG
    source = _get_source(config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog)


def _people_record(identifier, **overrides):
    record = {
        "people_id": identifier,
        "name": "Ada Lovelace",
        "department_id": 7,
        "department": "Engineering",
        "people_type_id": 1,
        "wk_day_hrs": {"mon": 8, "tue": 8, "wed": 8, "thu": 8, "fri": 8},
        "capacity": 160.0,
        "timeoff": 8.0,
        "scheduled": 140.0,
        "billable": 120.0,
        "nonBillable": 20.0,
        "overtime": 0.0,
        "unscheduled": 12.0,
    }
    record.update(overrides)
    return record


def _project_record(identifier, **overrides):
    record = {
        "project_id": identifier,
        "name": "Analytical Engine",
        "client_id": 42,
        "scheduled": 320.0,
        "billable": 300.0,
        "nonBillable": 20.0,
    }
    record.update(overrides)
    return record


def _record_for(root_key, identifier, **overrides):
    builder = _people_record if root_key == "people" else _project_record
    return builder(identifier, **overrides)


def _query_params(request):
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


@pytest.fixture(scope="module")
def manifest():
    with open(_MANIFEST_PATH) as manifest_file:
        return yaml.safe_load(manifest_file)


# --- discovery -----------------------------------------------------------------------------


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_report_stream_is_discoverable(stream_name, path, root_key):
    """Both report streams are exposed by the manifest."""
    stream_names = [stream.name for stream in _get_source().streams(_CONFIG)]
    assert stream_name in stream_names


def test_existing_streams_are_unchanged():
    """Adding the report streams does not remove or rename any pre-existing stream."""
    stream_names = sorted(stream.name for stream in _get_source().streams(_CONFIG))
    assert stream_names == sorted(_EXISTING_STREAMS + ["reports-people", "reports-projects"])


@pytest.mark.parametrize(
    "stream_name, expected_primary_key",
    [
        pytest.param("reports-people", [["people_id"]], id="reports-people"),
        pytest.param("reports-projects", [["project_id"]], id="reports-projects"),
    ],
)
def test_report_stream_primary_key(stream_name, expected_primary_key):
    stream = next(stream for stream in _get_source().streams(_CONFIG) if stream.name == stream_name)
    assert stream.as_airbyte_stream().source_defined_primary_key == expected_primary_key


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_report_stream_is_full_refresh_only(stream_name, path, root_key):
    """The Reports API has no cursor field; the streams must not declare incremental sync."""
    stream = next(stream for stream in _get_source().streams(_CONFIG) if stream.name == stream_name)
    assert not stream.cursor_field


# --- record extraction ---------------------------------------------------------------------


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_records_are_unwrapped_from_root_key(stream_name, path, root_key):
    """Records nested under the `people` / `projects` root key are extracted by the DpathExtractor."""
    response = {root_key: [_record_for(root_key, 1), _record_for(root_key, 2)]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _sync(stream_name)

    identifier_field = "people_id" if root_key == "people" else "project_id"
    assert [record.record.data[identifier_field] for record in output.records] == [1, 2]


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_empty_report_emits_no_records(stream_name, path, root_key):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: []})
        output = _sync(stream_name)

    assert output.records == []
    assert not output.errors


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_records_outside_root_key_are_ignored(stream_name, path, root_key):
    """Sibling keys in the payload (e.g. request echo / totals) must not be emitted as records."""
    response = {
        root_key: [_record_for(root_key, 1)],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "totals": {"scheduled": 140.0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _sync(stream_name)

    assert len(output.records) == 1


@pytest.mark.parametrize(
    "field, value",
    [
        pytest.param("people_id", 99, id="people_id"),
        pytest.param("name", "Grace Hopper", id="name"),
        pytest.param("department_id", 3, id="department_id"),
        pytest.param("department", "Research", id="department"),
        pytest.param("people_type_id", 2, id="people_type_id"),
        pytest.param("wk_day_hrs", {"mon": 4, "tue": 4}, id="wk_day_hrs"),
        pytest.param("capacity", 80.0, id="capacity"),
        pytest.param("timeoff", 16.0, id="timeoff"),
        pytest.param("scheduled", 64.0, id="scheduled"),
        pytest.param("billable", 40.5, id="billable"),
        pytest.param("nonBillable", 23.5, id="nonBillable"),
        pytest.param("overtime", 2.25, id="overtime"),
        pytest.param("unscheduled", 0.0, id="unscheduled"),
    ],
)
def test_reports_people_preserves_schema_fields(field, value):
    """Every documented `reports-people` property survives extraction."""
    response = {"people": [_people_record(1, **{field: value})]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/reports/people", json=response)
        output = _sync("reports-people")

    assert len(output.records) == 1
    assert output.records[0].record.data[field] == value


@pytest.mark.parametrize(
    "field, value",
    [
        pytest.param("project_id", 77, id="project_id"),
        pytest.param("name", "Difference Engine", id="name"),
        pytest.param("client_id", 5, id="client_id"),
        pytest.param("scheduled", 12.5, id="scheduled"),
        pytest.param("billable", 10.0, id="billable"),
        pytest.param("nonBillable", 2.5, id="nonBillable"),
    ],
)
def test_reports_projects_preserves_schema_fields(field, value):
    """Every documented `reports-projects` property survives extraction."""
    response = {"projects": [_project_record(1, **{field: value})]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/reports/projects", json=response)
        output = _sync("reports-projects")

    assert len(output.records) == 1
    assert output.records[0].record.data[field] == value


@pytest.mark.parametrize(
    "stream_name, path, root_key, nullable_field",
    [
        pytest.param("reports-people", "/reports/people", "people", "capacity", id="reports-people"),
        pytest.param("reports-projects", "/reports/projects", "projects", "client_id", id="reports-projects"),
    ],
)
def test_null_valued_fields_do_not_break_extraction(stream_name, path, root_key, nullable_field):
    """Report payloads may contain nulls; the record is still emitted, minus the null field.

    Every schema property is nullable, so a null must not fail schema validation. Null values
    are dropped during record serialization, hence the `not in` assertion.
    """
    response = {root_key: [_record_for(root_key, 1, **{nullable_field: None})]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _sync(stream_name)

    assert len(output.records) == 1
    assert nullable_field not in output.records[0].record.data
    assert not output.errors


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_declared_schema_matches_emitted_record(stream_name, path, root_key):
    """The inline schema declares every field the stream emits for a full report record."""
    record = _record_for(root_key, 1)

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: [record]})
        output = _sync(stream_name)

    stream = next(stream for stream in _get_source().streams(_CONFIG) if stream.name == stream_name)
    declared_properties = set(stream.get_json_schema()["properties"])
    assert set(record) <= declared_properties
    assert set(output.records[0].record.data) <= declared_properties


# --- request shape -------------------------------------------------------------------------


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_start_date_is_trimmed_to_calendar_date(stream_name, path, root_key):
    """`config.start_date` is a date-time, but the Reports API expects `YYYY-MM-DD`."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: []})
        _sync(stream_name)

        assert _query_params(mocker.last_request)["start_date"] == "2024-01-01"


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_end_date_from_config_is_used(stream_name, path, root_key):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: []})
        _sync(stream_name)

        assert _query_params(mocker.last_request)["end_date"] == "2024-12-31"


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_end_date_defaults_to_today_when_not_configured(stream_name, path, root_key):
    """Without `end_date`, the manifest falls back to `now_utc()` formatted as `YYYY-MM-DD`."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: []})
        _sync(stream_name, config=_CONFIG_NO_END_DATE)

        end_date = _query_params(mocker.last_request)["end_date"]

    now = datetime.now(tz=timezone.utc)
    # Accept the next day too, in case the UTC date rolls over mid-test.
    allowed = {now.strftime("%Y-%m-%d"), (now + timedelta(days=1)).strftime("%Y-%m-%d")}
    assert end_date in allowed


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_custom_start_date_flows_into_request(stream_name, path, root_key):
    config = {**_CONFIG, "start_date": "2025-06-15T09:30:00Z", "end_date": "2025-07-15"}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: []})
        _sync(stream_name, config=config)

        params = _query_params(mocker.last_request)

    assert params["start_date"] == "2025-06-15"
    assert params["end_date"] == "2025-07-15"


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_report_stream_does_not_paginate(stream_name, path, root_key):
    """Report endpoints do not support pagination: exactly one request, and no page params.

    The mock returns a full-looking page twice; a paginating stream would request page 2 and
    emit duplicate records.
    """
    page = {root_key: [_record_for(root_key, identifier) for identifier in range(1, 201)]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", [{"json": page, "status_code": 200}] * 2)
        output = _sync(stream_name)

        requests_made = [request for request in mocker.request_history if request.path == f"/v3{path}"]

    assert len(requests_made) == 1
    assert len(output.records) == 200
    params = _query_params(requests_made[0])
    assert "page" not in params
    assert "per-page" not in params


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_report_stream_sends_bearer_auth(stream_name, path, root_key):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: []})
        _sync(stream_name)

        assert mocker.last_request.headers["Authorization"] == "Bearer test_access_token"


# --- spec ----------------------------------------------------------------------------------


def test_end_date_is_declared_optional_in_spec(manifest):
    """`end_date` must not be required, so existing Float configs keep working."""
    connection_specification = manifest["spec"]["connection_specification"]

    assert "end_date" in connection_specification["properties"]
    assert "end_date" not in connection_specification["required"]


def test_end_date_spec_pattern_accepts_calendar_dates(manifest):
    end_date_spec = manifest["spec"]["connection_specification"]["properties"]["end_date"]

    assert end_date_spec["type"] == "string"
    assert end_date_spec["pattern"] == r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
