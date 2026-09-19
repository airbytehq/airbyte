# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `actions` and `follow-ups` streams on `source-incident-io`.

Verifies that both streams read from the paginated `/v3` endpoints (the `/v2`
endpoints are deprecated), follow the `pagination_meta.after` cursor, and stop
when no `after` value is returned.
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
        mocker.get(
            f"{_BASE_URL}{path}",
            [{"json": first_response}, {"json": second_response}],
        )
        output = _read_stream(stream_name)

        requests_made = mocker.request_history

    assert [message.record.data["id"] for message in output.records] == ["a-1", "a-2"]
    assert len(requests_made) == 2
    assert requests_made[0].qs["page_size"] == ["100"]
    assert "after" not in requests_made[0].qs
    assert requests_made[1].qs["after"] == ["a-1"]
    assert requests_made[1].qs["page_size"] == ["100"]
    assert all("/v2/" not in request.path for request in requests_made)


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

        assert len(mocker.request_history) == 1

    assert [message.record.data["id"] for message in output.records] == ["a-1"]


def test_follow_ups_record_keeps_category():
    category = {"id": "c1", "name": "Bug", "description": "d", "rank": 1}
    response = {
        "follow_ups": [{"id": "fu-1", "category": category}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v3/follow_ups", json=response)
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

    assert connection_status.status == Status.SUCCEEDED
