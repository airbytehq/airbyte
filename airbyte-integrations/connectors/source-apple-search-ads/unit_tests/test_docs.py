# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Checks that docs/integrations/sources/apple-search-ads.md agrees with manifest.yaml
on stream keys and on which spec fields are required.
"""

import re
from pathlib import Path

import pytest
import yaml


CONNECTOR_DIR = Path(__file__).parent.parent
MANIFEST_PATH = CONNECTOR_DIR / "manifest.yaml"
DOCS_PATH = CONNECTOR_DIR.parents[2] / "docs" / "integrations" / "sources" / "apple-search-ads.md"

NONE_MARKER = "None"


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def docs():
    if not DOCS_PATH.exists():
        pytest.skip(f"Docs file not found at {DOCS_PATH}")
    return DOCS_PATH.read_text()


def _table_rows(docs, header_first_cell):
    """Return the body rows of the first Markdown table whose header starts with header_first_cell."""
    lines = docs.splitlines()
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and cells[0] == header_first_cell:
            rows = []
            for row in lines[i + 2 :]:
                if not row.lstrip().startswith("|"):
                    break
                rows.append([c.strip() for c in row.strip().strip("|").split("|")])
            return rows
    raise AssertionError(f"No table with first header cell {header_first_cell!r} in {DOCS_PATH.name}")


def _codes(cell):
    return re.findall(r"`([^`]+)`", cell)


def _manifest_streams(manifest):
    return {s["name"]: s for s in manifest["definitions"]["streams"].values()}


def _manifest_primary_key(stream):
    pk = stream.get("primary_key")
    if not pk:
        return []
    return [pk] if isinstance(pk, str) else list(pk)


def _manifest_cursor_field(stream):
    incremental = stream.get("incremental_sync")
    return incremental.get("cursor_field") if incremental else None


def test_stream_table_lists_every_manifest_stream(manifest, docs):
    documented = {_codes(row[0])[0] for row in _table_rows(docs, "Stream")}
    assert documented == set(_manifest_streams(manifest))


def test_stream_table_primary_keys_match_manifest(manifest, docs):
    streams = _manifest_streams(manifest)
    for row in _table_rows(docs, "Stream"):
        name = _codes(row[0])[0]
        expected = _manifest_primary_key(streams[name])
        documented = _codes(row[1])
        assert documented == expected, f"{name}: docs primary key {documented or NONE_MARKER} != manifest {expected or NONE_MARKER}"
        if not expected:
            assert row[1].startswith(NONE_MARKER), f"{name}: primary key cell must say {NONE_MARKER!r}"


def test_stream_table_cursor_fields_match_manifest(manifest, docs):
    streams = _manifest_streams(manifest)
    for row in _table_rows(docs, "Stream"):
        name = _codes(row[0])[0]
        expected = _manifest_cursor_field(streams[name])
        documented = _codes(row[2])
        assert documented == ([expected] if expected else []), f"{name}: docs cursor {documented} != manifest {expected}"


def test_reference_table_required_column_matches_spec(manifest, docs):
    spec = manifest["spec"]["connection_specification"]
    rows = {_codes(row[0])[0]: row[1] for row in _table_rows(docs, "Field")}
    assert set(rows) == set(spec["properties"])
    for field, required_cell in rows.items():
        expected = "Yes" if field in spec.get("required", []) else "No"
        assert required_cell == expected, f"{field}: docs Required {required_cell!r} != spec {expected!r}"
