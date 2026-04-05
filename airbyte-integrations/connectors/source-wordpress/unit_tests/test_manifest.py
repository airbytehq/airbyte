# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-wordpress manifest.yaml.

Validates:
1. Incremental streams have lookback_window: PT1H to mitigate DST data loss.
2. No field_name values contain tab characters (regression for pages stream bug).
"""

import pathlib

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _get_stream_def(manifest, stream_name):
    return manifest["definitions"]["streams"][stream_name]


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("editor_blocks", id="editor_blocks"),
        pytest.param("comments", id="comments"),
        pytest.param("pages", id="pages"),
        pytest.param("media", id="media"),
    ],
)
def test_incremental_stream_has_lookback_window(manifest, stream_name):
    """Each incremental stream must define lookback_window: PT1H to cover DST transitions."""
    stream = _get_stream_def(manifest, stream_name)
    inc = stream.get("incremental_sync", {})
    assert inc.get("lookback_window") == "PT1H", (
        f"Stream '{stream_name}' should have lookback_window=PT1H, " f"got {inc.get('lookback_window')!r}"
    )


def test_pages_modified_after_field_name_has_no_tab(manifest):
    """Regression: pages stream field_name must not contain a tab character."""
    pages = _get_stream_def(manifest, "pages")
    field_name = pages["incremental_sync"]["start_time_option"]["field_name"]
    assert "\t" not in field_name, f"pages stream field_name contains a tab character: {field_name!r}"
    assert field_name == "modified_after"


def test_no_field_names_contain_tabs_anywhere(manifest):
    """Walk the entire manifest and ensure no field_name value contains a tab."""
    violations = []
    _check_for_tab_in_field_names(manifest, path="", violations=violations)
    assert not violations, "Found tab characters in field_name values:\n" + "\n".join(f"  - {v}" for v in violations)


def _check_for_tab_in_field_names(obj, path, violations):
    """Recursively walk a dict/list and flag any field_name containing a tab."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key == "field_name" and isinstance(value, str) and "\t" in value:
                violations.append(f"{current_path} = {value!r}")
            _check_for_tab_in_field_names(value, current_path, violations)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _check_for_tab_in_field_names(item, f"{path}[{i}]", violations)
