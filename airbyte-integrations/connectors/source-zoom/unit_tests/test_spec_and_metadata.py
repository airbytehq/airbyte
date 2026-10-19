# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CI_MANIFEST_DIR = Path("/airbyte/integration_code/source_declarative_manifest")
_MANIFEST_DIR = _CI_MANIFEST_DIR if _CI_MANIFEST_DIR.exists() else Path(__file__).parent.parent
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.yaml"
_METADATA_PATH = _MANIFEST_DIR / "metadata.yaml"
_TOKEN_URL = "https://zoom.us/oauth/token"
_USERS_URL = "https://api.zoom.us/v2/users"
_CONFIG = {
    "account_id": "test_account_id",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
}


def test_connection_spec_has_titled_fields_and_optional_hidden_authorization_endpoint():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    specification = manifest["spec"]["connection_specification"]
    properties = specification["properties"]

    assert all(property_spec.get("title") for property_spec in properties.values())
    assert "authorization_endpoint" not in specification["required"]
    assert properties["authorization_endpoint"]["airbyte_hidden"] is True
    assert properties["authorization_endpoint"]["default"] == _TOKEN_URL


def test_full_refresh_uses_default_token_endpoint_when_not_configured():
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    catalog = CatalogBuilder().with_stream("users", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        token_mock = mocker.post(
            _TOKEN_URL,
            json={"access_token": "test_access_token", "token_type": "bearer", "expires_in": 3599},
        )
        mocker.get(_USERS_URL, json={"users": [{"id": "u1", "email": "a@example.com"}], "next_page_token": ""})

        output = read(source, _CONFIG, catalog)

    assert token_mock.call_count == 1
    assert len(output.records) == 1
    assert output.errors == []


def test_metadata_has_registry_hosts_heartbeat_and_suggested_streams():
    if not _METADATA_PATH.exists():
        pytest.skip("metadata.yaml is not available next to manifest.yaml")

    metadata = yaml.safe_load(_METADATA_PATH.read_text())["data"]
    suggested_streams = [
        "users",
        "meetings",
        "meeting_registrants",
        "report_meetings",
        "report_meeting_participants",
    ]

    assert metadata["allowedHosts"]["hosts"] == ["api.zoom.us", "zoom.us"]
    assert metadata["maxSecondsBetweenMessages"] == 5400
    assert metadata["suggestedStreams"]["streams"] == suggested_streams

    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    manifest_stream_names = {stream["name"] for stream in manifest["streams"]}
    assert set(suggested_streams).issubset(manifest_stream_names)
