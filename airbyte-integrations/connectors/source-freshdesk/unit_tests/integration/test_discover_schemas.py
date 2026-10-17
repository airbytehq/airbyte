# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

from config_builder import ConfigBuilder

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.test.entrypoint_wrapper import discover


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))


def test_discovered_cursor_fields_are_declared_in_their_schemas() -> None:
    config = ConfigBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH))
    output = discover(source, config)
    streams = {stream.name: stream for stream in output.catalog.catalog.streams}

    for stream in streams.values():
        if stream.source_defined_cursor and stream.default_cursor_field:
            cursor_field = stream.default_cursor_field[0]
            properties = stream.json_schema.get("properties", {})
            assert cursor_field in properties, (
                f"Stream {stream.name!r} declares cursor {cursor_field!r} " "but its top-level JSON schema does not include it"
            )

    assert (
        "ticket_updated_at" in streams["conversations"].json_schema["properties"]
    ), "Stream 'conversations' schema must declare ticket_updated_at"
    assert (
        "executed_at_cursor" in streams["time_entries"].json_schema["properties"]
    ), "Stream 'time_entries' schema must declare executed_at_cursor"
    assert (
        "ticket_updated_at" not in streams["business_hours"].json_schema["properties"]
    ), "Stream 'business_hours' schema must not declare ticket_updated_at"
