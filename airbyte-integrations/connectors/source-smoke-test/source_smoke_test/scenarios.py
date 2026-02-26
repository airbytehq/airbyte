#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
"""Predefined smoke test scenarios for destination regression testing.

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


def get_scenario_records(
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    """Get records for a scenario, using generator if specified."""
    if scenario.get("record_generator") == "large_batch":
        return generate_large_batch_records(scenario)
    return scenario.get("records", [])
