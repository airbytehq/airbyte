# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Predefined smoke test scenarios for destination regression testing.

Vendored from PyAirbyte `airbyte/cli/smoke_test_source/_scenarios.py` (v0.46.0) to drop the PyAirbyte dependency.

Each scenario defines a stream name, JSON schema, optional primary key,
and either inline records or a record generator reference.
"""

from __future__ import annotations

import math
from typing import Any


_DEFAULT_LARGE_BATCH_COUNT = 1000

HIGH_VOLUME_SCENARIO_NAMES: set[str] = {
    "large_batch_stream",
}

PREDEFINED_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "basic_types",
        "description": "Covers fundamental column types: string, integer, number, boolean.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "amount": {"type": "number"},
                "is_active": {"type": "boolean"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "name": "Alice", "amount": 100.50, "is_active": True},
            {"id": 2, "name": "Bob", "amount": 0.0, "is_active": False},
            {"id": 3, "name": "", "amount": -99.99, "is_active": True},
        ],
    },
    {
        "name": "timestamp_types",
        "description": "Covers date and timestamp formats including ISO 8601 variations.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "created_date": {"type": "string", "format": "date"},
                "updated_at": {"type": "string", "format": "date-time"},
                "epoch_seconds": {"type": "integer"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "created_date": "2024-01-15",
                "updated_at": "2024-01-15T10:30:00Z",
                "epoch_seconds": 1705312200,
            },
            {
                "id": 2,
                "created_date": "1970-01-01",
                "updated_at": "1970-01-01T00:00:00+00:00",
                "epoch_seconds": 0,
            },
            {
                "id": 3,
                "created_date": "2099-12-31",
                "updated_at": "2099-12-31T23:59:59.999999Z",
                "epoch_seconds": 4102444799,
            },
        ],
    },
    {
        "name": "large_decimals_and_numbers",
        "description": ("Tests handling of very large numbers, high precision decimals, and boundary values."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "big_integer": {"type": "integer"},
                "precise_decimal": {"type": "number"},
                "small_decimal": {"type": "number"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "big_integer": 9999999999999999,
                "precise_decimal": math.pi,
                "small_decimal": 0.000001,
            },
            {
                "id": 2,
                "big_integer": -9999999999999999,
                "precise_decimal": -0.1,
                "small_decimal": 1e-10,
            },
            {
                "id": 3,
                "big_integer": 0,
                "precise_decimal": 99999999.99999999,
                "small_decimal": 0.0,
            },
        ],
    },
    {
        "name": "nested_json_objects",
        "description": "Tests nested object and array handling in destination columns.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "nested_deep": {
                    "type": "object",
                    "properties": {
                        "level1": {
                            "type": "object",
                            "properties": {
                                "level2": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
                "items_array": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {"type": "string"},
                            "qty": {"type": "integer"},
                        },
                    },
                },
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "metadata": {"source": "api", "tags": ["a", "b", "c"]},
                "nested_deep": {"level1": {"level2": {"value": "deep"}}},
                "items_array": [{"sku": "ABC", "qty": 10}],
            },
            {
                "id": 2,
                "metadata": {"source": "manual", "tags": []},
                "nested_deep": {"level1": {"level2": {"value": ""}}},
                "items_array": [],
            },
        ],
    },
    {
        "name": "null_handling",
        "description": "Tests null values across all column types and patterns.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "nullable_string": {"type": ["null", "string"]},
                "nullable_integer": {"type": ["null", "integer"]},
                "nullable_number": {"type": ["null", "number"]},
                "nullable_boolean": {"type": ["null", "boolean"]},
                "nullable_object": {
                    "type": ["null", "object"],
                    "properties": {"key": {"type": "string"}},
                },
                "always_null": {"type": ["null", "string"]},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "nullable_string": "present",
                "nullable_integer": 42,
                "nullable_number": math.pi,
                "nullable_boolean": True,
                "nullable_object": {"key": "val"},
                "always_null": None,
            },
            {
                "id": 2,
                "nullable_string": None,
                "nullable_integer": None,
                "nullable_number": None,
                "nullable_boolean": None,
                "nullable_object": None,
                "always_null": None,
            },
            {
                "id": 3,
                "nullable_string": "",
                "nullable_integer": 0,
                "nullable_number": 0.0,
                "nullable_boolean": False,
                "nullable_object": {},
                "always_null": None,
            },
        ],
    },
    {
        "name": "column_naming_edge_cases",
        "description": ("Tests special characters, casing, and reserved words in column names."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "CamelCaseColumn": {"type": "string"},
                "ALLCAPS": {"type": "string"},
                "snake_case_column": {"type": "string"},
                "column-with-dashes": {"type": "string"},
                "column.with.dots": {"type": "string"},
                "column with spaces": {"type": "string"},
                "select": {"type": "string"},
                "from": {"type": "string"},
                "order": {"type": "string"},
                "group": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "CamelCaseColumn": "camel",
                "ALLCAPS": "caps",
                "snake_case_column": "snake",
                "column-with-dashes": "dashes",
                "column.with.dots": "dots",
                "column with spaces": "spaces",
                "select": "reserved_select",
                "from": "reserved_from",
                "order": "reserved_order",
                "group": "reserved_group",
            },
        ],
    },
    {
        "name": "table_naming_edge_cases",
        "description": ("Stream with special characters in the name to test table naming."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "value": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "value": "table_name_test"},
        ],
    },
    {
        "name": "CamelCaseStreamName",
        "description": "Stream with CamelCase name to test case handling.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "value": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "value": "camel_case_stream_test"},
        ],
    },
    {
        "name": "wide_table_50_columns",
        "description": "Tests a wide table with 50 columns.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                **{f"col_{i:03d}": {"type": ["null", "string"]} for i in range(1, 50)},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                **{f"col_{i:03d}": f"val_{i}" for i in range(1, 50)},
            },
            {
                "id": 2,
                **{f"col_{i:03d}": None for i in range(1, 50)},
            },
        ],
    },
    {
        "name": "empty_stream",
        "description": ("A stream that emits zero records, testing empty dataset handling."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "value": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [],
    },
    {
        "name": "single_record_stream",
        "description": "A stream with exactly one record.",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "value": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "value": "only_record"},
        ],
    },
    {
        "name": "large_batch_stream",
        "description": ("A stream that generates a configurable number of records for batch testing."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "value": {"type": "number"},
                "category": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "record_count": _DEFAULT_LARGE_BATCH_COUNT,
        "record_generator": "large_batch",
        "high_volume": True,
    },
    {
        "name": "unicode_and_special_strings",
        "description": ("Tests unicode characters, emoji, escape sequences, and special string values."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "unicode_text": {"type": "string"},
                "special_chars": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "unicode_text": "Hello World",
                "special_chars": "line1\nline2\ttab",
            },
            {
                "id": 2,
                "unicode_text": "Caf\u00e9 na\u00efve r\u00e9sum\u00e9",
                "special_chars": 'quote"inside',
            },
            {
                "id": 3,
                "unicode_text": "\u4f60\u597d\u4e16\u754c",
                "special_chars": "back\\slash",
            },
            {
                "id": 4,
                "unicode_text": "\u0410\u0411\u0412\u0413",
                "special_chars": "",
            },
        ],
    },
    {
        "name": "schema_with_no_primary_key",
        "description": ("A stream without a primary key, testing append-only behavior."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
                "event_type": {"type": "string"},
                "payload": {"type": "string"},
            },
        },
        "primary_key": None,
        "records": [
            {"event_id": "evt_001", "event_type": "click", "payload": "{}"},
            {"event_id": "evt_001", "event_type": "click", "payload": "{}"},
            {
                "event_id": "evt_002",
                "event_type": "view",
                "payload": '{"page": "home"}',
            },
        ],
    },
    {
        "name": "long_column_names",
        "description": ("Tests handling of very long column names that may exceed database limits."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "a_very_long_column_name_that_exceeds"
                "_typical_database_limits_and_should_be"
                "_truncated_or_handled_gracefully_by"
                "_the_destination": {
                    "type": "string",
                },
                "another_extremely_verbose_column_name"
                "_designed_to_test_the_absolute_maximum"
                "_length_that_any_reasonable_database"
                "_would_support": {
                    "type": "string",
                },
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "a_very_long_column_name_that_exceeds"
                "_typical_database_limits_and_should_be"
                "_truncated_or_handled_gracefully_by"
                "_the_destination": "long_col_1",
                "another_extremely_verbose_column_name"
                "_designed_to_test_the_absolute_maximum"
                "_length_that_any_reasonable_database"
                "_would_support": "long_col_2",
            },
        ],
    },
    {
        "name": "duplicate_primary_keys",
        "description": (
            "Tests dedup behavior when multiple records share the same primary key. " "Destinations should keep the latest record per key."
        ),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "updated_value": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "name": "Alice", "updated_value": "first"},
            {"id": 2, "name": "Bob", "updated_value": "first"},
            {"id": 1, "name": "Alice", "updated_value": "second"},
            {"id": 3, "name": "Charlie", "updated_value": "first"},
            {"id": 2, "name": "Bob", "updated_value": "second"},
            {"id": 1, "name": "Alice", "updated_value": "third"},
        ],
    },
    {
        "name": "time_types",
        "description": ("Tests time-with-timezone and time-without-timezone formats. " "These are commonly mishandled by destinations."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "time_no_tz": {
                    "type": "string",
                    "format": "time",
                    "airbyte_type": "time_without_timezone",
                },
                "time_with_tz": {
                    "type": "string",
                    "format": "time",
                    "airbyte_type": "time_with_timezone",
                },
                "timestamp_no_tz": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_without_timezone",
                },
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "time_no_tz": "10:30:00",
                "time_with_tz": "10:30:00+05:30",
                "timestamp_no_tz": "2024-01-15T10:30:00",
            },
            {
                "id": 2,
                "time_no_tz": "00:00:00",
                "time_with_tz": "00:00:00Z",
                "timestamp_no_tz": "1970-01-01T00:00:00",
            },
            {
                "id": 3,
                "time_no_tz": "23:59:59.999999",
                "time_with_tz": "23:59:59.999999-08:00",
                "timestamp_no_tz": "2099-12-31T23:59:59.999999",
            },
        ],
    },
    {
        "name": "union_types",
        "description": (
            "Tests columns with oneOf/anyOf schemas where a field can hold "
            "values of different types. Union handling is a frequent source "
            "of destination bugs."
        ),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "string_or_integer": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                "number_or_null": {"oneOf": [{"type": "number"}, {"type": "null"}]},
                "object_or_string": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {"key": {"type": "string"}},
                        },
                        {"type": "string"},
                    ],
                },
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "string_or_integer": "hello",
                "number_or_null": math.pi,
                "object_or_string": {"key": "value"},
            },
            {
                "id": 2,
                "string_or_integer": 42,
                "number_or_null": None,
                "object_or_string": "just_a_string",
            },
            {
                "id": 3,
                "string_or_integer": "",
                "number_or_null": 0.0,
                "object_or_string": {},
            },
        ],
    },
    {
        "name": "array_of_primitives",
        "description": (
            "Tests arrays containing primitive types (strings, integers, mixed). "
            "Complements nested_json_objects which only tests arrays of objects."
        ),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "string_array": {"type": "array", "items": {"type": "string"}},
                "integer_array": {"type": "array", "items": {"type": "integer"}},
                "mixed_array": {"type": "array"},
                "empty_typed_array": {"type": "array", "items": {"type": "number"}},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {
                "id": 1,
                "string_array": ["a", "b", "c"],
                "integer_array": [1, 2, 3],
                "mixed_array": ["text", 42, True, None, math.pi],
                "empty_typed_array": [],
            },
            {
                "id": 2,
                "string_array": [],
                "integer_array": [0, -1, 999999999],
                "mixed_array": [{"nested": "object"}, [1, 2]],
                "empty_typed_array": [0.0, 1e10, -99.99],
            },
            {
                "id": 3,
                "string_array": ["", "  ", "normal"],
                "integer_array": [],
                "mixed_array": [],
                "empty_typed_array": [math.pi],
            },
        ],
    },
    {
        "name": "large_string_values",
        "description": ("Tests handling of very long string values that may exceed " "column size limits or buffer sizes in destinations."),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "short_value": {"type": "string"},
                "medium_value": {"type": "string"},
                "large_value": {"type": "string"},
            },
        },
        "primary_key": [["id"]],
        "record_generator": "large_strings",
    },
    {
        "name": "sparse_records",
        "description": (
            "Tests records where different rows have different subsets "
            "of columns populated. Destinations must handle missing "
            "fields gracefully."
        ),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "col_a": {"type": ["null", "string"]},
                "col_b": {"type": ["null", "integer"]},
                "col_c": {"type": ["null", "number"]},
                "col_d": {"type": ["null", "boolean"]},
                "col_e": {"type": ["null", "string"]},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "col_a": "only_a"},
            {"id": 2, "col_b": 42},
            {"id": 3, "col_c": math.pi},
            {"id": 4, "col_d": True},
            {"id": 5, "col_e": "only_e"},
            {
                "id": 6,
                "col_a": "all",
                "col_b": 99,
                "col_c": 1.0,
                "col_d": False,
                "col_e": "present",
            },
            {"id": 7},
        ],
    },
    {
        "name": "special_number_values",
        "description": (
            "Tests boundary and special numeric values including very large "
            "and very small floats. These commonly break destinations that "
            "use fixed-precision numeric types."
        ),
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "float_value": {"type": "number"},
                "integer_value": {"type": "integer"},
            },
        },
        "primary_key": [["id"]],
        "records": [
            {"id": 1, "float_value": 1.7976931348623157e308, "integer_value": 1},
            {"id": 2, "float_value": 5e-324, "integer_value": -1},
            {"id": 3, "float_value": -1.7976931348623157e308, "integer_value": 0},
            {"id": 4, "float_value": -5e-324, "integer_value": 9223372036854775807},
            {"id": 5, "float_value": 0.0, "integer_value": -9223372036854775808},
            {"id": 6, "float_value": 1.0, "integer_value": 2147483647},
            {"id": 7, "float_value": -1.0, "integer_value": -2147483648},
        ],
    },
]


def generate_large_batch_records(
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate records for the large_batch_stream scenario."""
    count = scenario.get("record_count", _DEFAULT_LARGE_BATCH_COUNT)
    categories = ["cat_a", "cat_b", "cat_c", "cat_d", "cat_e"]
    return [
        {
            "id": i,
            "name": f"record_{i:06d}",
            "value": float(i) * 1.1,
            "category": categories[i % len(categories)],
        }
        for i in range(1, count + 1)
    ]


def generate_large_string_records() -> list[dict[str, Any]]:
    """Generate records with progressively larger string values.

    Produces strings of ~1 KB, ~10 KB, and ~100 KB to test column size
    limits and buffer handling in destinations.
    """
    return [
        {
            "id": 1,
            "short_value": "x" * 1_000,
            "medium_value": "y" * 10_000,
            "large_value": "z" * 100_000,
        },
        {
            "id": 2,
            "short_value": "Hello, World!",
            "medium_value": ("The quick brown fox jumps over the lazy dog. " * 250).strip(),
            "large_value": ("Pack my box with five dozen liquor jugs. " * 2500).strip(),
        },
    ]


def get_scenario_records(
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    """Get records for a scenario, using generator if specified."""
    generator = scenario.get("record_generator")
    if generator == "large_batch":
        return generate_large_batch_records(scenario)
    if generator == "large_strings":
        return generate_large_string_records()
    return scenario.get("records", [])
