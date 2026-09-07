# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-airtable manifest.yaml types_mapping.

Validates that multipleLookupValues, lookup, and rollup type mappings
cover all known Airtable result types and include a catch-all fallback
to prevent ValueError when unknown result types are encountered.
"""

import pathlib

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture(scope="module")
def types_mapping(manifest):
    return manifest["definitions"]["streams"]["airtable_stream"]["schema_loader"]["schema_type_identifier"]["types_mapping"]


def _get_entries_for_type(types_mapping, current_type):
    """Get all TypesMap entries for a given current_type."""
    return [entry for entry in types_mapping if entry.get("current_type") == current_type]


def _get_catch_all_entry(entries):
    """Get the catch-all entry (no condition) that is NOT the 'not result' entry."""
    catch_alls = [e for e in entries if "condition" not in e or e["condition"] is None]
    return catch_alls


# Types that previously caused ValueError because they were not in any condition
PREVIOUSLY_MISSING_RESULT_TYPES = ["aiText", "formula", "lookup", "rollup", "manualSort", "linkToRecord", "multipleLookupValues"]


@pytest.mark.parametrize(
    "current_type",
    [
        pytest.param("multipleLookupValues", id="multipleLookupValues"),
        pytest.param("lookup", id="lookup"),
        pytest.param("rollup", id="rollup"),
    ],
)
def test_type_has_catch_all_fallback(types_mapping, current_type):
    """Each compound type must have a condition-less catch-all entry as the last entry."""
    entries = _get_entries_for_type(types_mapping, current_type)
    assert len(entries) > 0, f"No entries found for current_type={current_type}"

    last_entry = entries[-1]
    assert "condition" not in last_entry or last_entry["condition"] is None, (
        f"The last TypesMap entry for '{current_type}' must be a condition-less catch-all, "
        f"but it has condition: {last_entry.get('condition')!r}"
    )

    # Catch-all should default to array of string
    target = last_entry["target_type"]
    assert target == {
        "field_type": "array",
        "items": "string",
    }, f"Catch-all for '{current_type}' should map to array of string, got {target!r}"


@pytest.mark.parametrize(
    "current_type,missing_type",
    [
        pytest.param(ct, mt, id=f"{ct}-covers-{mt}")
        for ct in ["multipleLookupValues", "lookup", "rollup"]
        for mt in PREVIOUSLY_MISSING_RESULT_TYPES
    ],
)
def test_string_condition_covers_previously_missing_types(types_mapping, current_type, missing_type):
    """The string-array condition for each compound type must include previously missing result types."""
    entries = _get_entries_for_type(types_mapping, current_type)

    # Find the first entry (string-type array condition)
    string_entry = entries[0]
    condition = string_entry.get("condition", "")

    assert (
        missing_type in condition
    ), f"TypesMap for '{current_type}' string-array condition does not include '{missing_type}'. Condition: {condition!r}"


@pytest.mark.parametrize(
    "current_type",
    [
        pytest.param("multipleLookupValues", id="multipleLookupValues"),
        pytest.param("lookup", id="lookup"),
        pytest.param("rollup", id="rollup"),
    ],
)
def test_all_entries_have_valid_target_types(types_mapping, current_type):
    """All entries for compound types must have target_type with field_type: array."""
    entries = _get_entries_for_type(types_mapping, current_type)
    for i, entry in enumerate(entries):
        target = entry["target_type"]
        assert isinstance(target, dict), f"Entry {i} for '{current_type}' should have a dict target_type (array), got {target!r}"
        assert target.get("field_type") == "array", f"Entry {i} for '{current_type}' should have field_type=array, got {target!r}"


@pytest.mark.parametrize(
    "result_type,expected_items_type",
    [
        pytest.param("aiText", "string", id="aiText-maps-to-string"),
        pytest.param("formula", "string", id="formula-maps-to-string"),
        pytest.param("lookup", "string", id="lookup-nested-maps-to-string"),
        pytest.param("rollup", "string", id="rollup-nested-maps-to-string"),
        pytest.param("manualSort", "string", id="manualSort-maps-to-string"),
        pytest.param("linkToRecord", "string", id="linkToRecord-maps-to-string"),
        pytest.param("multipleLookupValues", "string", id="multipleLookupValues-nested-maps-to-string"),
        pytest.param("number", "number", id="number-maps-to-number"),
        pytest.param("checkbox", "boolean", id="checkbox-maps-to-boolean"),
        pytest.param("date", "date", id="date-maps-to-date"),
        pytest.param("dateTime", "timestamp_with_timezone", id="dateTime-maps-to-timestamp"),
        pytest.param("multipleSelects", {"field_type": "array", "items": "string"}, id="multipleSelects-maps-to-array-string"),
    ],
)
def test_multipleLookupValues_result_type_resolves(types_mapping, result_type, expected_items_type):
    """Verify that multipleLookupValues entries cover specific result types correctly."""
    entries = _get_entries_for_type(types_mapping, "multipleLookupValues")

    # Simulate condition evaluation: find which entry matches this result_type
    matching_entry = None
    for entry in entries:
        condition = entry.get("condition")
        if condition is None:
            # Catch-all matches everything
            if matching_entry is None:
                matching_entry = entry
            break
        if f"'{result_type}'" in condition:
            matching_entry = entry
            break

    assert matching_entry is not None, f"No TypesMap entry for multipleLookupValues matches result type '{result_type}'"

    target = matching_entry["target_type"]
    assert (
        target.get("items") == expected_items_type
    ), f"multipleLookupValues with result type '{result_type}' should map items to {expected_items_type!r}, got {target.get('items')!r}"
