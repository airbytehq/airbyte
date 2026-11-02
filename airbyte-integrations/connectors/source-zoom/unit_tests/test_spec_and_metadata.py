# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml


_CI_MANIFEST_DIR = Path("/airbyte/integration_code/source_declarative_manifest")
_MANIFEST_DIR = _CI_MANIFEST_DIR if _CI_MANIFEST_DIR.exists() else Path(__file__).parent.parent
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.yaml"
_METADATA_PATH = _MANIFEST_DIR / "metadata.yaml"
_TOKEN_URL = "https://zoom.us/oauth/token"


def test_connection_spec_has_titled_fields_and_optional_hidden_authorization_endpoint():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    specification = manifest["spec"]["connection_specification"]
    properties = specification["properties"]

    assert all(property_spec.get("title") for property_spec in properties.values())
    credentials_options = properties["credentials"]["oneOf"]
    for option in credentials_options:
        assert all(property_spec.get("title") for property_spec in option["properties"].values())

    server_to_server = next(
        (option for option in credentials_options if option["properties"]["auth_type"].get("const") == "server_to_server"),
        None,
    )
    assert server_to_server is not None
    assert "authorization_endpoint" not in server_to_server.get("required", [])
    authorization_endpoint = server_to_server["properties"]["authorization_endpoint"]
    assert authorization_endpoint["airbyte_hidden"] is True
    assert authorization_endpoint["default"] == _TOKEN_URL


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
