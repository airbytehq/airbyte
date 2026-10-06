# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `actions` and `follow-ups` streams on `source-incident-io`.

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


def _get_source():
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )


def _read_stream(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(_get_source(), _CONFIG, catalog)


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
    assert all(request.qs["page_size"] == ["100"] for request in requests_made)
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


def test_check_uses_v3_actions():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v3/actions",
            json={"actions": [], "pagination_meta": {}},
        )
        connection_status = _get_source().check(logging.getLogger("airbyte"), _CONFIG)

        assert len(mocker.request_history) >= 1
        assert mocker.request_history[0].path == "/v3/actions"
        assert "incident_mode" in mocker.request_history[0].qs

    assert connection_status.status == Status.SUCCEEDED
