# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the incident.io alerting and escalation streams."""

from pathlib import Path

import pytest
import requests_mock

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
_CONFIG = {"api_key": "test-key"}
_BASE_URL = "https://api.incident.io"


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


@pytest.mark.parametrize(
    ("stream_name", "page_size"),
    [
        pytest.param("alert_routes", "50", id="alert-routes"),
        pytest.param("incident_alerts", "50", id="incident-alerts"),
        pytest.param("escalation_paths", "25", id="escalation-paths"),
    ],
)
def test_paginated_alerting_streams_follow_cursor(stream_name, page_size):
    first_id = f"{stream_name}-1"
    second_id = f"{stream_name}-2"
    responses = [
        {
            "json": {
                stream_name: [{"id": first_id}],
                "pagination_meta": {"after": "next-page", "page_size": int(page_size)},
            }
        },
        {"json": {stream_name: [{"id": second_id}], "pagination_meta": {"page_size": int(page_size)}}},
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/{stream_name}", responses)
        output = _read_stream(stream_name)
        requests_made = mocker.request_history

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [first_id, second_id]
    assert len(requests_made) == 2
    assert "after" not in requests_made[0].qs
    assert requests_made[1].qs["after"] == ["next-page"]
    assert all(request.qs["page_size"] == [page_size] for request in requests_made)
    if stream_name == "incident_alerts":
        assert all("incident_id" not in request.qs and "alert_id" not in request.qs for request in requests_made)


def test_alert_routes_stops_after_trailing_empty_page():
    responses = [
        {
            "json": {
                "alert_routes": [{"id": "route-1"}],
                "pagination_meta": {"after": "route-1", "page_size": 50},
            }
        },
        {"json": {"alert_routes": [], "pagination_meta": {"page_size": 50}}},
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/alert_routes", responses)
        output = _read_stream("alert_routes")
        requests_made = mocker.request_history

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["route-1"]
    assert len(requests_made) == 2
    assert requests_made[1].qs["after"] == ["route-1"]
    assert all(request.qs["page_size"] == ["50"] for request in requests_made)


def test_alert_sources_removes_secret_token():
    response = {
        "alert_sources": [
            {
                "id": "source-1",
                "name": "Email",
                "source_type": "email",
                "template": {},
                "secret_token": "must-not-be-emitted",
            }
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/alert_sources", json=response)
        output = _read_stream("alert_sources")

    assert output.errors == []
    assert len(output.records) == 1
    assert "secret_token" not in output.records[0].record.data


def test_incident_alerts_are_unpartitioned():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incident_alerts", json={"incident_alerts": [], "pagination_meta": {}})
        output = _read_stream("incident_alerts")
        requests_made = mocker.request_history

    assert output.errors == []
    assert len(requests_made) == 1
    assert "incident_id" not in requests_made[0].qs
    assert "alert_id" not in requests_made[0].qs
