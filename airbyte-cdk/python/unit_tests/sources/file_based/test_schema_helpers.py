#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.file_based.exceptions import SchemaInferenceError
from airbyte_cdk.sources.file_based.schema_helpers import ComparableType, conforms_to_schema, merge_schemas

COMPLETE_CONFORMING_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}


NONCONFORMING_EXTRA_COLUMN_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
    "column_x": "extra"
}

CONFORMING_WITH_MISSING_COLUMN_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
}

CONFORMING_WITH_NARROWER_TYPE_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": True,
    "number_field": True,
    "string_field": True,
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}

NONCONFORMING_WIDER_TYPE_RECORD = {
    "null_field": "not None",
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}

NONCONFORMING_NON_OBJECT_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": "not an object",
}

NONCONFORMING_NON_ARRAY_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": "not an array",
    "object_field": {"col": "val"},
}

CONFORMING_MIXED_TYPE_NARROWER_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}

NONCONFORMING_MIXED_TYPE_WIDER_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}

CONFORMING_MIXED_TYPE_WITHIN_TYPE_RANGE_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "val1",
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}

NONCONFORMING_INVALID_ARRAY_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": ["this should not be an array"],
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}

NONCONFORMING_TOO_WIDE_ARRAY_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "okay",
    "array_field": ["val1", "val2"],
    "object_field": {"col": "val"},
}


CONFORMING_NARROWER_ARRAY_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": "okay",
    "array_field": [1, 2],
    "object_field": {"col": "val"},
}


NONCONFORMING_INVALID_OBJECT_RECORD = {
    "null_field": None,
    "boolean_field": True,
    "integer_field": 1,
    "number_field": 1.5,
    "string_field": {"this": "should not be an object"},
    "array_field": [1.1, 2.2],
    "object_field": {"col": "val"},
}


SCHEMA = {
    "type": "object",
    "properties": {
        "null_field": {
            "type": "null"
        },
        "boolean_field": {
            "type": "boolean"
        },
        "integer_field": {
            "type": "integer"
        },
        "number_field": {
            "type": "number"
        },
        "string_field": {
            "type": "string"
        },
        "array_field": {
            "type": "array",
            "items": {
                "type": "number",
            },
        },
        "object_field": {
            "type": "object"
        },
    }
}


@pytest.mark.parametrize(
    "record,schema,expected_result",
    [
        pytest.param(COMPLETE_CONFORMING_RECORD, SCHEMA, True, id="record-conforms"),
        pytest.param(NONCONFORMING_EXTRA_COLUMN_RECORD, SCHEMA, False, id="nonconforming-extra-column"),
        pytest.param(CONFORMING_WITH_MISSING_COLUMN_RECORD, SCHEMA, True, id="record-conforms-with-missing-column"),
        pytest.param(CONFORMING_WITH_NARROWER_TYPE_RECORD, SCHEMA, True, id="record-conforms-with-narrower-type"),
        pytest.param(NONCONFORMING_WIDER_TYPE_RECORD, SCHEMA, False, id="nonconforming-wider-type"),
        pytest.param(NONCONFORMING_NON_OBJECT_RECORD, SCHEMA, False, id="nonconforming-string-is-not-an-object"),
        pytest.param(NONCONFORMING_NON_ARRAY_RECORD, SCHEMA, False, id="nonconforming-string-is-not-an-array"),
        pytest.param(NONCONFORMING_TOO_WIDE_ARRAY_RECORD, SCHEMA, False, id="nonconforming-array-values-too-wide"),
        pytest.param(CONFORMING_NARROWER_ARRAY_RECORD, SCHEMA, True, id="conforming-array-values-narrower-than-schema"),
        pytest.param(NONCONFORMING_INVALID_ARRAY_RECORD, SCHEMA, False, id="nonconforming-array-is-not-a-string"),
        pytest.param(NONCONFORMING_INVALID_OBJECT_RECORD, SCHEMA, False, id="nonconforming-object-is-not-a-string"),
    ]
)
def test_conforms_to_schema(
    record: Mapping[str, Any],
    schema: Mapping[str, Any],
    expected_result: bool
):
    assert conforms_to_schema(record, schema) == expected_result


def test_comparable_types():
    assert ComparableType.OBJECT > ComparableType.STRING
    assert ComparableType.STRING > ComparableType.NUMBER
    assert ComparableType.NUMBER > ComparableType.INTEGER
    assert ComparableType.INTEGER > ComparableType.BOOLEAN
    assert ComparableType["OBJECT"] == ComparableType.OBJECT


@pytest.mark.parametrize(
    "schema1,schema2,expected_result",
    [
        pytest.param({}, {}, {}, id="empty-schemas"),
        pytest.param({"a": None}, {}, None, id="null-value-in-schema"),
        pytest.param({"a": {"type": "integer"}}, {}, {"a": {"type": "integer"}}, id="single-key-schema1"),
        pytest.param({}, {"a": {"type": "integer"}}, {"a": {"type": "integer"}}, id="single-key-schema2"),
        pytest.param({"a": {"type": "integer"}}, {"a": {"type": "integer"}}, {"a": {"type": "integer"}}, id="single-key-both-schemas"),
        pytest.param({"a": {"type": "integer"}}, {"a": {"type": "number"}}, {"a": {"type": "number"}}, id="single-key-schema2-is-wider"),
        pytest.param({"a": {"type": "number"}}, {"a": {"type": "integer"}}, {"a": {"type": "number"}}, id="single-key-schema1-is-wider"),
        pytest.param({"a": {"type": "array"}}, {"a": {"type": "integer"}}, None, id="single-key-with-array-schema1"),
        pytest.param({"a": {"type": "integer"}}, {"a": {"type": "array"}}, None, id="single-key-with-array-schema2"),
        pytest.param({"a": {"type": "object", "properties": {"b": {"type": "integer"}}}}, {"a": {"type": "object", "properties": {"b": {"type": "integer"}}}}, {"a": {"type": "object", "properties": {"b": {"type": "integer"}}}}, id="single-key-same-object"),
        pytest.param({"a": {"type": "object", "properties": {"b": {"type": "integer"}}}}, {"a": {"type": "object", "properties": {"b": {"type": "string"}}}}, None, id="single-key-different-objects"),
        pytest.param({"a": {"type": "object", "properties": {"b": {"type": "integer"}}}}, {"a": {"type": "number"}}, None, id="single-key-with-object-schema1"),
        pytest.param({"a": {"type": "number"}}, {"a": {"type": "object", "properties": {"b": {"type": "integer"}}}}, None, id="single-key-with-object-schema2"),
        pytest.param({"a": {"type": "array", "items": {"type": "number"}}}, {"a": {"type": "array", "items": {"type": "number"}}}, {"a": {"type": "array", "items": {"type": "number"}}}, id="equal-arrays-in-both-schemas"),
        pytest.param({"a": {"type": "array", "items": {"type": "integer"}}}, {"a": {"type": "array", "items": {"type": "number"}}}, None, id="different-arrays-in-both-schemas"),
        pytest.param({"a": {"type": "integer"}, "b": {"type": "string"}}, {"c": {"type": "number"}}, {"a": {"type": "integer"}, "b": {"type": "string"}, "c": {"type": "number"}}, id=""),
        pytest.param({"a": {"type": "invalid_type"}}, {"b": {"type": "integer"}}, None, id="invalid-type"),
    ]
)
def test_merge_schemas(schema1, schema2, expected_result):
    if expected_result is not None:
        assert merge_schemas(schema1, schema2) == expected_result
    else:
        with pytest.raises(SchemaInferenceError):
            merge_schemas(schema1, schema2)
