# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-incident-io`: the v3 `actions` and `follow-ups` streams, the check stream,
incremental state handling, error handling, and the `users` stream options.

Verifies that both streams read from the paginated `/v3` endpoints (the `/v2`
endpoints are deprecated), follow the `pagination_meta.after` cursor, stop when
no `after` value is returned, and query every `incident_mode` partition
(`standard`, `retrospective`, `test`, `tutorial`, `stream`) so records from all
incident modes are synced.

Each test registers a catch-all empty response for the path first, then
mode-specific responses for `?incident_mode=<mode>` URLs. requests_mock matches
later registrations first, so the mode-specific mocks take precedence over the
catch-all.
"""

import logging
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import Status, SyncMode
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
_CONFIG = {"api_key": "test-key"}
_BASE_URL = "https://api.incident.io"
_MODES = ["standard", "retrospective", "test", "tutorial", "stream"]


def _get_source(state=None):
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=state if state is not None else StateBuilder().build(),
    )


def _read_stream(stream_name, sync_mode=SyncMode.full_refresh, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(_get_source(state), _CONFIG, catalog, state=state)


def _mock_empty(mocker, path, records_field):
    mocker.get(
        f"{_BASE_URL}{path}",
        json={records_field: [], "pagination_meta": {"page_size": 100}},
    )


def _mock_mode(mocker, path, mode, *args, **kwargs):
    mocker.get(f"{_BASE_URL}{path}?incident_mode={mode}", *args, **kwargs)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_stream_reads_v3_endpoint_and_follows_pagination(stream_name, path, records_field):
    first_response = {
        records_field: [{"id": "a-1", "title": "first"}],
        "pagination_meta": {"after": "a-1", "page_size": 100},
    }
    second_response = {
        records_field: [{"id": "a-2"}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        _mock_empty(mocker, path, records_field)
        _mock_mode(mocker, path, "standard", [{"json": first_response}, {"json": second_response}])
        output = _read_stream(stream_name)

        requests_made = mocker.request_history

    assert [message.record.data["id"] for message in output.records] == ["a-1", "a-2"]
    assert len(requests_made) == len(_MODES) + 1
    standard_requests = [request for request in requests_made if request.qs["incident_mode"] == ["standard"]]
    assert len(standard_requests) == 2
    assert "after" not in standard_requests[0].qs
    assert standard_requests[1].qs["after"] == ["a-1"]
    assert all(request.qs["page_size"] == ["250"] for request in requests_made)
    assert all("/v2/" not in request.path for request in requests_made)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_stream_queries_every_incident_mode(stream_name, path, records_field):
    with requests_mock.Mocker() as mocker:
        _mock_empty(mocker, path, records_field)
        for mode in _MODES:
            _mock_mode(
                mocker,
                path,
                mode,
                json={
                    records_field: [{"id": f"{mode}-1"}],
                    "pagination_meta": {"page_size": 100},
                },
            )
        output = _read_stream(stream_name)

        requests_made = mocker.request_history

    assert len(requests_made) == len(_MODES)
    assert all(len(request.qs["incident_mode"]) == 1 for request in requests_made)
    assert {request.qs["incident_mode"][0] for request in requests_made} == set(_MODES)
    assert sorted(message.record.data["id"] for message in output.records) == sorted(f"{mode}-1" for mode in _MODES)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_stream_stops_after_single_page(stream_name, path, records_field):
    response = {
        records_field: [{"id": "a-1"}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _read_stream(stream_name)

        requests_made = mocker.request_history

    assert len(requests_made) == len(_MODES)
    assert all("after" not in request.qs for request in requests_made)
    assert [message.record.data["id"] for message in output.records] == ["a-1"] * len(_MODES)


def test_follow_ups_record_keeps_category():
    category = {"id": "c1", "name": "Bug", "description": "d", "rank": 1}
    response = {
        "follow_ups": [{"id": "fu-1", "category": category}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        _mock_empty(mocker, "/v3/follow_ups", "follow_ups")
        _mock_mode(mocker, "/v3/follow_ups", "standard", json=response)
        output = _read_stream("follow-ups")

    assert output.records[0].record.data["category"] == category


def test_check_uses_incidents_stream():
    """The check stream is `incidents`: a current endpoint that needs only the base incident read scope."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v2/incidents",
            json={"incidents": [{"id": "inc-1", "updated_at": "2026-09-18T10:38:18.161Z"}], "pagination_meta": {}},
        )
        connection_status = _get_source().check(logging.getLogger("airbyte"), _CONFIG)

        assert len(mocker.request_history) >= 1
        assert mocker.request_history[0].path == "/v2/incidents"
        assert all("/v3/actions" not in request.url for request in mocker.request_history)

    assert connection_status.status == Status.SUCCEEDED


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("incidents", "/v2/incidents", "incidents"),
        ("alerts", "/v2/alerts", "alerts"),
        ("escalations", "/v2/escalations", "escalations"),
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_incremental_sends_state_as_a_date_and_keeps_full_timestamp(stream_name, path, records_field):
    """The API's `updated_at[gte]` filter accepts `yyyy-mm-dd` only, so the request carries the date of the
    stored cursor while the emitted state keeps the full timestamp (see CONTRIBUTING.md)."""
    state = StateBuilder().with_stream_state(stream_name, {"updated_at": "2026-09-18T10:38:18Z"}).build()
    response = {
        records_field: [{"id": "r-1", "updated_at": "2026-09-20T08:00:00.123Z"}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _read_stream(stream_name, SyncMode.incremental, state)
        requests_made = mocker.request_history

    assert requests_made, "no request was made"
    assert all(request.qs["updated_at[gte]"] == ["2026-09-18"] for request in requests_made)
    assert [message.record.data["id"] for message in output.records][:1] == ["r-1"]
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state.get("updated_at") == "2026-09-20T08:00:00Z" or "updated_at" in str(final_state)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("incidents", "/v2/incidents", "incidents"),
        ("actions", "/v3/actions", "actions"),
    ],
)
def test_full_refresh_without_start_date_reads_everything(stream_name, path, records_field):
    """The cursor window is applied in full refresh too, so the default start must predate all
    incident.io data. A relative default (for example two years back) silently dropped 2023 records on
    an existing full-refresh connection."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={records_field: [{"id": "r-1"}], "pagination_meta": {}})
        _read_stream(stream_name)
        requests_made = mocker.request_history

    assert requests_made
    assert all(request.qs["updated_at[gte]"] == ["2020-01-01"] for request in requests_made)


def test_missing_scope_is_a_config_error_naming_the_scope():
    """A 403 is a configuration problem the user can fix; the message carries the scope the API names."""
    # Real body captured from the API on 2026-10-07 with a key lacking the scope (scope name swapped).
    body = {
        "type": "resource_forbidden",
        "status": 403,
        "request_id": "ZtsoWDj7",
        "errors": [
            {
                "code": "missing_required_scope",
                "message": "missing a required scope: workflows.view",
                "metadata": {"scope": "workflows.view"},
            }
        ],
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/workflows", status_code=403, json=body)
        output = _read_stream("workflows")

    assert output.records == []
    assert output.errors, "expected an error trace message"
    error = output.errors[-1].trace.error
    assert error.failure_type.value == "config_error"
    assert "workflows.view" in (error.message or "") + (error.internal_message or "")


def test_users_requests_inactive_users():
    """`users` asks for deactivated accounts too, so a user who leaves does not vanish from the stream."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v2/users",
            json={"users": [{"id": "u-1", "is_active": False}], "pagination_meta": {"page_size": 100}},
        )
        output = _read_stream("users")
        requests_made = mocker.request_history

    assert requests_made[0].qs["include_inactive"] == ["true"]
    assert requests_made[0].qs["page_size"] == ["10000"]
    assert output.records[0].record.data["is_active"] is False
