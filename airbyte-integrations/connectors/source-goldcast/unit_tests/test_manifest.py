# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards that `event_members.props` stays schemaless.

`props` carries Goldcast registration form fields, which every workspace defines for itself.
Enumerating them can only ever be correct for the workspaces that happen to be listed: on a V2
destination an undeclared property is dropped without appearing in `_airbyte_meta.changes[]`,
so any other workspace loses its fields silently. Declaring `props` as a schemaless object makes
the destination serialise it to a JSON string, preserving every key whatever it is named.

These tests fail if a future edit re-introduces an enumerated list, and if the two copies of the
`event_members` schema in the manifest ever drift apart.
"""

from pathlib import Path

import pytest
import yaml


EVENT_MEMBERS_STREAM_INDEX = 6


@pytest.fixture(scope="module")
def manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return yaml.safe_load(manifest_path.read_text())


@pytest.fixture(scope="module")
def definitions_schema(manifest: dict) -> dict:
    return manifest["definitions"]["event_members_stream"]["schema_loader"]["schema"]


@pytest.fixture(scope="module")
def stream_schema(manifest: dict) -> dict:
    stream = manifest["streams"][EVENT_MEMBERS_STREAM_INDEX]
    assert stream["name"] == "event_members", "stream order changed; update EVENT_MEMBERS_STREAM_INDEX"
    return stream["schema_loader"]["schema"]


@pytest.mark.parametrize("fixture_name", ["definitions_schema", "stream_schema"])
def test_props_is_schemaless(fixture_name: str, request) -> None:
    """An enumerated `props` silently drops every registration field it does not list."""
    schema = request.getfixturevalue(fixture_name)
    props = schema["properties"]["props"]

    assert props == {
        "type": "object"
    }, f"`props` must stay a schemaless object so workspace-defined registration fields survive; got {props!r}"


def test_both_event_members_schema_copies_agree(definitions_schema: dict, stream_schema: dict) -> None:
    """The manifest declares this schema twice; an edit to one copy only would be a silent bug."""
    assert definitions_schema == stream_schema
