#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Union

import dpath.util
import jsonschema
import pytest
from airbyte_protocol.models import AirbyteCatalog
from live_tests.commons.models import ExecutionResult
from live_tests.utils import fail_test_on_failing_execution_results, find_all_values_for_key_in_schema

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.allow_diagnostic_mode
async def test_discover(
    record_property: Callable,
    discover_target_execution_result: ExecutionResult,
    target_discovered_catalog: AirbyteCatalog,
):
    """
    Verify that the discover command succeeds on the target connection.

    Success is determined by the presence of a catalog with one or more streams, all with unique names.
    """
    fail_test_on_failing_execution_results(
        record_property,
        [discover_target_execution_result],
    )
    duplicated_stream_names = _duplicated_stream_names(target_discovered_catalog.streams)

    assert target_discovered_catalog is not None, "Message should have catalog"
    assert hasattr(target_discovered_catalog, "streams") and target_discovered_catalog.streams, "Catalog should contain streams"
    assert len(duplicated_stream_names) == 0, f"Catalog should have uniquely named streams, duplicates are: {duplicated_stream_names}"


def _duplicated_stream_names(streams) -> List[str]:
    """Counts number of times a stream appears in the catalog"""
    name_counts = dict()
    for stream in streams:
        count = name_counts.get(stream.name, 0)
        name_counts[stream.name] = count + 1
    return [k for k, v in name_counts.items() if v > 1]


@pytest.mark.allow_diagnostic_mode
async def test_streams_have_valid_json_schemas(target_discovered_catalog: AirbyteCatalog):
    """Check if all stream schemas are valid json schemas."""
    for stream in target_discovered_catalog.streams:
        jsonschema.Draft7Validator.check_schema(stream.json_schema)


@pytest.mark.allow_diagnostic_mode
async def test_defined_cursors_exist_in_schema(target_discovered_catalog: AirbyteCatalog):
    """Check if all of the source defined cursor fields exist on stream's json schema."""
    for stream in target_discovered_catalog.streams:
        if not stream.default_cursor_field:
            continue
        schema = stream.json_schema
        assert "properties" in schema, f"Top level item should have an 'object' type for {stream.name} stream schema"
        cursor_path = "/properties/".join(stream.default_cursor_field)
        cursor_field_location = dpath.util.search(schema["properties"], cursor_path)
        assert cursor_field_location, (
            f"Some of defined cursor fields {stream.default_cursor_field} are not specified in discover schema "
            f"properties for {stream.name} stream"
        )


@pytest.mark.allow_diagnostic_mode
async def test_defined_refs_exist_in_schema(target_discovered_catalog: AirbyteCatalog):
    """Check the presence of unresolved `$ref`s values within each json schema."""
    schemas_errors = []
    for stream in target_discovered_catalog.streams:
        check_result = list(find_all_values_for_key_in_schema(stream.json_schema, "$ref"))
        if check_result:
            schemas_errors.append({stream.name: check_result})

    assert not schemas_errors, f"Found unresolved `$refs` values for selected streams: {tuple(schemas_errors)}."


@pytest.mark.allow_diagnostic_mode
@pytest.mark.parametrize("keyword", ["allOf", "not"])
async def test_defined_keyword_exist_in_schema(keyword, target_discovered_catalog: AirbyteCatalog):
    """Check for the presence of not allowed keywords within each json schema"""
    schemas_errors = []
    for stream in target_discovered_catalog.streams:
        check_result = _find_keyword_schema(stream.json_schema, key=keyword)
        if check_result:
            schemas_errors.append(stream.name)

    assert not schemas_errors, f"Found not allowed `{keyword}` keyword for selected streams: {schemas_errors}."


def _find_keyword_schema(schema: Union[dict, list, str], key: str) -> bool:
    """Find at least one keyword in a schema, skip object properties"""

    def _find_keyword(schema, key, _skip=False):
        if isinstance(schema, list):
            for v in schema:
                _find_keyword(v, key)
        elif isinstance(schema, dict):
            for k, v in schema.items():
                if k == key and not _skip:
                    raise StopIteration
                rec_skip = k == "properties" and schema.get("type") == "object"
                _find_keyword(v, key, rec_skip)

    try:
        _find_keyword(schema, key)
    except StopIteration:
        return True
    return False


@pytest.mark.allow_diagnostic_mode
async def test_primary_keys_exist_in_schema(target_discovered_catalog: AirbyteCatalog):
    """Check that all primary keys are present in catalog."""
    for stream in target_discovered_catalog.streams:
        for pk in stream.source_defined_primary_key or []:
            schema = stream.json_schema
            pk_path = "/properties/".join(pk)
            pk_field_location = dpath.util.search(schema["properties"], pk_path)
            assert pk_field_location, f"One of the PKs ({pk}) is not specified in discover schema for {stream.name} stream"


@pytest.mark.allow_diagnostic_mode
async def test_streams_has_sync_modes(target_discovered_catalog: AirbyteCatalog):
    """Check that the supported_sync_modes is a not empty field in streams of the catalog."""
    for stream in target_discovered_catalog.streams:
        assert stream.supported_sync_modes is not None, f"The stream {stream.name} is missing supported_sync_modes field declaration."
        assert len(stream.supported_sync_modes) > 0, f"supported_sync_modes list on stream {stream.name} should not be empty."


@pytest.mark.allow_diagnostic_mode
async def test_additional_properties_is_true(target_discovered_catalog: AirbyteCatalog):
    """
    Check that value of the "additionalProperties" field is always true.

    A stream schema declaring "additionalProperties": false introduces the risk of accidental breaking changes.
    Specifically, when removing a property from the stream schema, existing connector catalog will no longer be valid.
    False value introduces the risk of accidental breaking changes.

    Read https://github.com/airbytehq/airbyte/issues/14196 for more details.
    """
    for stream in target_discovered_catalog.streams:
        additional_properties_values = list(find_all_values_for_key_in_schema(stream.json_schema, "additionalProperties"))
        if additional_properties_values:
            assert all(
                [additional_properties_value is True for additional_properties_value in additional_properties_values]
            ), "When set, additionalProperties field value must be true for backward compatibility."


@pytest.mark.allow_diagnostic_mode
@pytest.mark.skip("This a placeholder for a CAT which has too many failures. We need to fix the connectors at scale first.")
async def test_catalog_has_supported_data_types(target_discovered_catalog: AirbyteCatalog):
    """
    Check that all streams have supported data types, format and airbyte_types.

    Supported data types are listed there: https://docs.airbyte.com/understanding-airbyte/supported-data-types/
    """
    pass
