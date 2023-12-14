#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Mapping

import pytest
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer

NOW = 1234567


@pytest.mark.parametrize(
    "input_records,expected_schemas",
    [
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc"}},
                {"stream": "my_stream", "data": {"field_A": "def"}},
            ],
            {"my_stream": {"field_A": {"type": "string"}}},
            id="test_basic",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": 1.0}},
                {"stream": "my_stream", "data": {"field_A": "abc"}},
            ],
            {"my_stream": {"field_A": {"type": ["number", "string"]}}},
            id="test_deriving_schema_refine",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"obj": {"data": [1.0, 2.0, 3.0]}}},
                {"stream": "my_stream", "data": {"obj": {"other_key": "xyz"}}},
            ],
            {
                "my_stream": {
                    "obj": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "array", "items": {"type": "number"}},
                            "other_key": {"type": "string"},
                        },
                    }
                }
            },
            id="test_derive_schema_for_nested_structures",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": 1}},
                {"stream": "my_stream", "data": {"field_A": 2}},
            ],
            {"my_stream": {"field_A": {"type": "number"}}},
            id="test_integer_number",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
            ],
            {"my_stream": {}},
            id="test_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": "abc"}},
            ],
            {"my_stream": {"field_A": {"type": ["null", "string"]}}},
            id="test_null_optional",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc"}}},
            ],
            {"my_stream": {"field_A": {"type": ["object", "null"], "properties": {"nested": {"type": "string"}}}}},
            id="test_any_of",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc", "nully": None}}},
            ],
            {"my_stream": {"field_A": {"type": ["object", "null"], "properties": {"nested": {"type": "string"}}}}},
            id="test_any_of_with_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc", "nully": None}}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc", "nully": "a string"}}},
            ],
            {
                "my_stream": {
                    "field_A": {
                        "type": ["object", "null"],
                        "properties": {"nested": {"type": "string"}, "nully": {"type": ["null", "string"]}},
                    }
                }
            },
            id="test_any_of_with_null_union",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc", "nully": "a string"}}},
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc", "nully": None}}},
            ],
            {
                "my_stream": {
                    "field_A": {
                        "type": ["object", "null"],
                        "properties": {"nested": {"type": "string"}, "nully": {"type": ["null", "string"]}},
                    }
                }
            },
            id="test_any_of_with_null_union_changed_order",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc", "nested": {"field_B": None}}},
            ],
            {"my_stream": {"field_A": {"type": "string"}, "nested": {"type": "object", "properties": {}}}},
            id="test_nested_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc", "nested": [{"field_B": None, "field_C": "abc"}]}},
            ],
            {
                "my_stream": {
                    "field_A": {"type": "string"},
                    "nested": {"type": "array", "items": {"type": "object", "properties": {"field_C": {"type": "string"}}}},
                }
            },
            id="test_array_nested_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc", "nested": None}},
                {"stream": "my_stream", "data": {"field_A": "abc", "nested": [{"field_B": None, "field_C": "abc"}]}},
            ],
            {
                "my_stream": {
                    "field_A": {"type": "string"},
                    "nested": {"type": ["array", "null"], "items": {"type": "object", "properties": {"field_C": {"type": "string"}}}},
                }
            },
            id="test_array_top_level_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": "abc"}},
            ],
            {"my_stream": {"field_A": {"type": ["null", "string"]}}},
            id="test_null_string",
        ),
    ],
)
def test_schema_derivation(input_records: List, expected_schemas: Mapping):
    inferrer = SchemaInferrer()
    for record in input_records:
        inferrer.accumulate(AirbyteRecordMessage(stream=record["stream"], data=record["data"], emitted_at=NOW))

    for stream_name, expected_schema in expected_schemas.items():
        assert inferrer.get_inferred_schemas()[stream_name] == {
            "$schema": "http://json-schema.org/schema#",
            "type": "object",
            "properties": expected_schema,
        }


def test_deriving_schema_multiple_streams():
    inferrer = SchemaInferrer()
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"field_A": 1.0}, emitted_at=NOW))
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream2", data={"field_A": "abc"}, emitted_at=NOW))
    inferred_schemas = inferrer.get_inferred_schemas()
    assert inferred_schemas["my_stream"] == {
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {"field_A": {"type": "number"}},
    }
    assert inferred_schemas["my_stream2"] == {
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {"field_A": {"type": "string"}},
    }


def test_get_individual_schema():
    inferrer = SchemaInferrer()
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"field_A": 1.0}, emitted_at=NOW))
    assert inferrer.get_stream_schema("my_stream") == {
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {"field_A": {"type": "number"}},
    }
    assert inferrer.get_stream_schema("another_stream") is None
