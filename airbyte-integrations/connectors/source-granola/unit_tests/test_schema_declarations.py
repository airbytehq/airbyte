# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the schema declarations in the Granola manifest."""

import os
from pathlib import Path

import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    configured_path = os.environ.get("SOURCE_GRANOLA_MANIFEST_PATH")
    if configured_path:
        return Path(configured_path)
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path / "manifest.yaml"
    return Path(__file__).parent.parent / "manifest.yaml"


_MANIFEST_PATH = _get_manifest_path()
_CONFIG = {"api_key": "test_api_key", "start_date": "2024-01-01"}
_BASE_URL = "https://public-api.granola.ai"


def _get_source():
    catalog = CatalogBuilder().build()
    state = StateBuilder().build()
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog,
        config=_CONFIG,
        state=state,
    )


def _read_records():
    notes = {
        "id": "not_test",
        "object": "note",
        "title": "Schema test note",
        "owner": {"name": "Test Owner", "email": "owner@example.com"},
        "created_at": "2024-01-02T03:04:05.000Z",
        "updated_at": "2024-01-02T03:05:06.000Z",
    }
    detailed_note = {
        **notes,
        "web_url": "https://notes.granola.ai/d/not_test",
        "calendar_event": {
            "event_title": "Schema test meeting",
            "invitees": [{"email": "owner@example.com"}],
            "organiser": "owner@example.com",
            "calendar_event_id": "event_test",
            "scheduled_start_time": "2024-01-02T03:00:00-08:00",
            "scheduled_end_time": "2024-01-02T04:00:00-08:00",
        },
        "attendees": [{"name": "Test Owner", "email": "owner@example.com"}],
        "folder_membership": [
            {
                "id": "folder_test",
                "object": "folder",
                "name": "Test folder",
                "parent_folder_id": None,
                "space_id": "space_test",
            }
        ],
        "space_membership": [{"object": "space", "id": "space_test", "name": "Test space"}],
        "summary_text": "Summary",
        "summary_markdown": "**Summary**",
        "transcript": [
            {
                "text": "Hello",
                "start_time": "2024-01-02T03:01:00.000Z",
                "end_time": "2024-01-02T03:01:01.000Z",
                "speaker": {"source": "speaker", "attribution": "them"},
            },
            {
                "text": "Hi",
                "start_time": "2024-01-02T03:01:02.000Z",
                "end_time": "2024-01-02T03:01:03.000Z",
                "speaker": {
                    "source": "microphone",
                    "diarization_label": "Speaker A",
                },
            },
        ],
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v1/notes",
            json={"notes": [notes], "cursor": "", "hasMore": False},
        )
        mocker.get(f"{_BASE_URL}/v1/notes/not_test", json=detailed_note)
        catalog = CatalogBuilder().with_stream("notes", SyncMode.full_refresh).with_stream("detailed_notes", SyncMode.full_refresh).build()
        output = read(_get_source(), _CONFIG, catalog)

    return [(record.record.stream, record.record.data) for record in output.records]


def _declared_paths(schema, prefix=""):
    paths = set()
    for name, property_schema in schema.get("properties", {}).items():
        path = f"{prefix}.{name}" if prefix else name
        paths.add(path)
        if "properties" in property_schema:
            paths.update(_declared_paths(property_schema, path))
        property_types = property_schema.get("type", [])
        if isinstance(property_types, str):
            property_types = [property_types]
        if "array" in property_types and "items" in property_schema:
            paths.update(_declared_paths(property_schema["items"], f"{path}[]"))
    return paths


def _record_paths(value, prefix=""):
    paths = set()
    if not isinstance(value, dict):
        return paths
    for name, child in value.items():
        path = f"{prefix}.{name}" if prefix else name
        paths.add(path)
        if isinstance(child, dict):
            paths.update(_record_paths(child, path))
        elif isinstance(child, list):
            for item in child:
                if isinstance(item, dict):
                    paths.update(_record_paths(item, f"{path}[]"))
    return paths


def _date_time_schemas(schema, prefix=""):
    for name, property_schema in schema.get("properties", {}).items():
        path = f"{prefix}.{name}" if prefix else name
        if property_schema.get("format") == "date-time":
            yield path, property_schema
        if "properties" in property_schema:
            yield from _date_time_schemas(property_schema, path)
        property_types = property_schema.get("type", [])
        if isinstance(property_types, str):
            property_types = [property_types]
        if "array" in property_types and "items" in property_schema:
            yield from _date_time_schemas(property_schema["items"], f"{path}[]")


def test_schema_declarations_cover_mocked_records():
    records = _read_records()
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    schemas = manifest["schemas"]

    for stream_name in ("notes", "detailed_notes"):
        declared_paths = _declared_paths(schemas[stream_name])
        stream_records = [data for stream, data in records if stream == stream_name]
        assert stream_records, f"{stream_name} emitted no records"
        undeclared_paths = set()
        for record in stream_records:
            undeclared_paths.update(_record_paths(record) - declared_paths)

        assert not undeclared_paths, f"{stream_name} emitted undeclared paths: {sorted(undeclared_paths)}"


def test_date_time_properties_declare_timezone_type():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    date_time_properties = [(path, schema) for schema in manifest["schemas"].values() for path, schema in _date_time_schemas(schema)]

    assert date_time_properties, "No date-time properties found in schemas"
    missing_timezone_type = [path for path, schema in date_time_properties if schema.get("airbyte_type") != "timestamp_with_timezone"]
    assert not missing_timezone_type, "Date-time properties missing airbyte_type: " f"{sorted(missing_timezone_type)}"
