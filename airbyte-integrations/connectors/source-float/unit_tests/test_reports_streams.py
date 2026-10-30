# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `reports-people` and `reports-projects` streams on `source-float`.

These streams read the Float Reports API (`GET /reports/people`, `GET /reports/projects`),
which differs from the other Float endpoints in four ways covered here:

* records are nested under a root key (`people` / `projects`) and unwrapped by a `DpathExtractor`,
* the date range is passed as `start_date` / `end_date` query params, derived from the config
  (`start_date` trimmed to `YYYY-MM-DD`, `end_date` defaulting to today via `now_utc()`),
* each row is a single aggregate for the whole requested range and carries no marker of the
  period it covers, so the requested range is stamped onto the record by `AddFields`,
* the endpoints do not support pagination, so the streams use `NoPagination`.
"""

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock
import yaml
from conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


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

# Added to every report record by the `AddFields` transformation, not returned by the API.
_PROVENANCE_FIELDS = {"start_date", "end_date"}

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


def _sync(stream_name, config=None):
    config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def _stream(stream_name, config=None):
    config = config or _CONFIG
    return next(stream for stream in get_source(config).streams(config) if stream.name == stream_name)


def _people_record(identifier, **overrides):
    record = {
        "people_id": identifier,
        "name": "Ada Lovelace",
        "department_id": 7,
        "department": "Engineering",
        "people_type_id": 1,
        # Deprecated Float field: keyed by the date the hours took effect, Sun-Sat.
        "wk_day_hrs": {"1970-01-01": [0, 8, 8, 8, 8, 8, 0]},
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
    with open(MANIFEST_PATH) as manifest_file:
        return yaml.safe_load(manifest_file)


# --- discovery -----------------------------------------------------------------------------


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_report_stream_is_discoverable(stream_name, path, root_key):
    """Both report streams are exposed by the manifest."""
    assert stream_name in [stream.name for stream in get_source(_CONFIG).streams(_CONFIG)]


def test_existing_streams_are_unchanged():
    """Adding the report streams does not remove or rename any pre-existing stream."""
    stream_names = sorted(stream.name for stream in get_source(_CONFIG).streams(_CONFIG))
    assert stream_names == sorted(_EXISTING_STREAMS + ["reports-people", "reports-projects"])


@pytest.mark.parametrize(
    "stream_name, expected_primary_key",
    [
        pytest.param("reports-people", [["people_id"]], id="reports-people"),
        pytest.param("reports-projects", [["project_id"]], id="reports-projects"),
    ],
)
def test_report_stream_primary_key(stream_name, expected_primary_key):
    assert _stream(stream_name).as_airbyte_stream().source_defined_primary_key == expected_primary_key


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_report_stream_is_full_refresh_only(stream_name, path, root_key):
    """The Reports API has no cursor field; the streams must not declare incremental sync."""
    assert not _stream(stream_name).cursor_field


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


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_null_valued_fields_do_not_break_extraction(stream_name, path, root_key):
    """Report payloads may contain nulls; the record is still emitted, minus the null field.

    Every schema property is nullable, so a null must not fail schema validation. Null values
    are dropped during record serialization, hence the `not in` assertion.
    """
    nullable_field = "capacity" if root_key == "people" else "client_id"
    response = {root_key: [_record_for(root_key, 1, **{nullable_field: None})]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _sync(stream_name)

    assert len(output.records) == 1
    assert nullable_field not in output.records[0].record.data
    assert not output.errors


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_declared_schema_matches_emitted_record(stream_name, path, root_key):
    """The inline schema declares exactly what the stream emits, and every value round-trips."""
    record = _record_for(root_key, 1)

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: [record]})
        output = _sync(stream_name)

    declared_properties = set(_stream(stream_name).get_json_schema()["properties"])
    emitted = output.records[0].record.data

    assert set(record) | _PROVENANCE_FIELDS == declared_properties
    assert set(emitted) == declared_properties
    # Extraction must not rewrite, coerce or drop any API-provided value.
    assert {key: emitted[key] for key in record} == record


# --- reporting period provenance -----------------------------------------------------------


@pytest.mark.parametrize("stream_name, path, root_key", _REPORT_STREAMS)
def test_records_carry_the_requested_reporting_period(stream_name, path, root_key):
    """Each aggregate row is stamped with the range it was computed for.

    The API returns one row per person/project for the whole requested range with no
    indication of that range, and the numbers change every sync, so without this stamp the
    emitted aggregates cannot be interpreted after the fact.
    """
    config = {**_CONFIG, "start_date": "2025-03-01T12:34:56Z", "end_date": "2025-03-31"}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={root_key: [_record_for(root_key, 1)]})
        output = _sync(stream_name, config=config)
        requested = _query_params(mocker.last_request)

    data = output.records[0].record.data
    assert data["start_date"] == "2025-03-01"
    assert data["end_date"] == "2025-03-31"
    # The stamp must be the range actually requested, not one computed independently.
    assert (data["start_date"], data["end_date"]) == (requested["start_date"], requested["end_date"])


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

    A single finite response, smaller than any plausible page size, keeps an accidentally
    configured paginator from looping. That way this fails on the injected page params rather
    than hanging on an unbounded sequence of requests.
    """
    page = {root_key: [_record_for(root_key, 1), _record_for(root_key, 2)]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", [{"json": page, "status_code": 200}])
        output = _sync(stream_name)

        requests_made = [request for request in mocker.request_history if request.path == f"/v3{path}"]

    assert len(requests_made) == 1
    assert len(output.records) == 2
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
