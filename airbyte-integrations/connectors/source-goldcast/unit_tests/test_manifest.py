# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards that `event_members.props` stays schemaless.

`props` carries Goldcast registration form fields, which every workspace defines for itself.
Enumerating them can only ever be correct for the workspaces that happen to be listed: on a V2
destination an undeclared property is dropped without appearing in `_airbyte_meta.changes[]`,
so any other workspace loses its fields silently. Declaring `props` as a schemaless object makes
the destination serialise it to a JSON string, preserving every key whatever it is named.

This test fails if a future edit re-introduces an enumerated list. It asserts on the `streams:`
entry, which is the schema the connector actually resolves — the manifest also carries an
unreferenced `definitions:` copy that nothing reads.
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="module")
def manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())


@pytest.fixture(scope="module")
def event_members_schema(manifest: dict) -> dict:
    """The `event_members` schema as the connector resolves it, looked up by name."""
    streams = [stream for stream in manifest["streams"] if stream.get("name") == "event_members"]
    assert len(streams) == 1, f"expected exactly one event_members stream, found {len(streams)}"
    return streams[0]["schema_loader"]["schema"]


def test_props_is_schemaless(event_members_schema: dict) -> None:
    """An enumerated `props` silently drops every registration field it does not list."""
    props = event_members_schema["properties"]["props"]

    assert props == {
        "type": "object"
    }, f"`props` must stay a schemaless object so workspace-defined registration fields survive; got {props!r}"
