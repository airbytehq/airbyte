#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Mapping

import pytest
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer, SchemaValidationException

NOW = 1234567


@pytest.mark.parametrize(
    "input_records,expected_schemas",
    [
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc"}},
                {"stream": "my_stream", "data": {"field_A": "def"}},
            ],
            {"my_stream": {"field_A": {"type": ["string", "null"]}}},
            id="test_basic",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": 1.0}},
                {"stream": "my_stream", "data": {"field_A": "abc"}},
            ],
            {"my_stream": {"field_A": {"type": ["number", "string", "null"]}}},
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
                        "type": ["object", "null"],
                        "properties": {
                            "data": {"type": ["array", "null"], "items": {"type": ["number", "null"]}},
                            "other_key": {"type": ["string", "null"]},
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
            {"my_stream": {"field_A": {"type": ["number", "null"]}}},
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
            {"my_stream": {"field_A": {"type": ["string", "null"]}}},
            id="test_null_optional",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc"}}},
            ],
            {"my_stream": {"field_A": {"type": ["object", "null"], "properties": {"nested": {"type": ["string", "null"]}}}}},
            id="test_any_of",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": {"nested": "abc", "nully": None}}},
            ],
            {"my_stream": {"field_A": {"type": ["object", "null"], "properties": {"nested": {"type": ["string", "null"]}}}}},
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
                        "properties": {"nested": {"type": ["string", "null"]}, "nully": {"type": ["string", "null"]}},
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
                        "properties": {"nested": {"type": ["string", "null"]}, "nully": {"type": ["string", "null"]}},
                    }
                }
            },
            id="test_any_of_with_null_union_changed_order",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc", "nested": {"field_B": None}}},
            ],
            {"my_stream": {"field_A": {"type": ["string", "null"]}, "nested": {"type": ["object", "null"], "properties": {}}}},
            id="test_nested_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": "abc", "nested": [{"field_B": None, "field_C": "abc"}]}},
            ],
            {
                "my_stream": {
                    "field_A": {"type": ["string", "null"]},
                    "nested": {"type": ["array", "null"], "items": {"type": ["object", "null"], "properties": {"field_C": {"type": ["string", "null"]}}}},
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
                    "field_A": {"type": ["string", "null"]},
                    "nested": {"type": ["array", "null"], "items": {"type": ["object", "null"], "properties": {"field_C": {"type": ["string", "null"]}}}},
                }
            },
            id="test_array_top_level_null",
        ),
        pytest.param(
            [
                {"stream": "my_stream", "data": {"field_A": None}},
                {"stream": "my_stream", "data": {"field_A": "abc"}},
            ],
            {"my_stream": {"field_A": {"type": ["string", "null"]}}},
            id="test_null_string",
        ),
    ],
)
def test_schema_derivation(input_records: List, expected_schemas: Mapping):
    inferrer = SchemaInferrer()
    for record in input_records:
        inferrer.accumulate(AirbyteRecordMessage(stream=record["stream"], data=record["data"], emitted_at=NOW))

    for stream_name, expected_schema in expected_schemas.items():
        assert inferrer.get_stream_schema(stream_name) == {
            "$schema": "http://json-schema.org/schema#",
            "type": "object",
            "properties": expected_schema,
        }


_STREAM_NAME = "a stream name"
_ANY_VALUE = "any value"
_IS_PK = True
_IS_CURSOR_FIELD = True


def _create_inferrer_with_required_field(is_pk: bool, field: List[List[str]]) -> SchemaInferrer:
    if is_pk:
        return SchemaInferrer(field)
    return SchemaInferrer([[]], field)


@pytest.mark.parametrize(
    "is_pk",
    [
        pytest.param(_IS_PK, id="required_field_is_pk"),
        pytest.param(_IS_CURSOR_FIELD, id="required_field_is_cursor_field"),
    ]
)
def test_field_is_on_root(is_pk: bool):
    inferrer = _create_inferrer_with_required_field(is_pk, [["property"]])

    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"property": _ANY_VALUE}, emitted_at=NOW))

    assert inferrer.get_stream_schema(_STREAM_NAME)["required"] == ["property"]
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property"]["type"] == "string"


@pytest.mark.parametrize(
    "is_pk",
    [
        pytest.param(_IS_PK, id="required_field_is_pk"),
        pytest.param(_IS_CURSOR_FIELD, id="required_field_is_cursor_field"),
    ]
)
def test_field_is_nested(is_pk: bool):
    inferrer = _create_inferrer_with_required_field(is_pk, [["property", "nested_property"]])

    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"property": {"nested_property": _ANY_VALUE}}, emitted_at=NOW))

    assert inferrer.get_stream_schema(_STREAM_NAME)["required"] == ["property"]
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property"]["type"] == "object"
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property"]["required"] == ["nested_property"]


@pytest.mark.parametrize(
    "is_pk",
    [
        pytest.param(_IS_PK, id="required_field_is_pk"),
        pytest.param(_IS_CURSOR_FIELD, id="required_field_is_cursor_field"),
    ]
)
def test_field_is_composite(is_pk: bool):
    inferrer = _create_inferrer_with_required_field(is_pk, [["property 1"], ["property 2"]])
    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"property 1": _ANY_VALUE, "property 2": _ANY_VALUE}, emitted_at=NOW))
    assert inferrer.get_stream_schema(_STREAM_NAME)["required"] == ["property 1", "property 2"]


@pytest.mark.parametrize(
    "is_pk",
    [
        pytest.param(_IS_PK, id="required_field_is_pk"),
        pytest.param(_IS_CURSOR_FIELD, id="required_field_is_cursor_field"),
    ]
)
def test_field_is_composite_and_nested(is_pk: bool):
    inferrer = _create_inferrer_with_required_field(is_pk, [["property 1", "nested"], ["property 2"]])

    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"property 1": {"nested": _ANY_VALUE}, "property 2": _ANY_VALUE}, emitted_at=NOW))

    assert inferrer.get_stream_schema(_STREAM_NAME)["required"] == ["property 1", "property 2"]
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property 1"]["type"] == "object"
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property 2"]["type"] == "string"
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property 1"]["required"] == ["nested"]
    assert inferrer.get_stream_schema(_STREAM_NAME)["properties"]["property 1"]["properties"]["nested"]["type"] == "string"


def test_given_pk_does_not_exist_when_get_inferred_schemas_then_raise_error():
    inferrer = SchemaInferrer([["pk does not exist"]])
    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"id": _ANY_VALUE}, emitted_at=NOW))

    with pytest.raises(SchemaValidationException) as exception:
        inferrer.get_stream_schema(_STREAM_NAME)

    assert len(exception.value.validation_errors) == 1


def test_given_pk_path_is_partially_valid_when_get_inferred_schemas_then_validation_error_mentions_where_the_issue_is():
    inferrer = SchemaInferrer([["id", "nested pk that does not exist"]])
    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"id": _ANY_VALUE}, emitted_at=NOW))

    with pytest.raises(SchemaValidationException) as exception:
        inferrer.get_stream_schema(_STREAM_NAME)

    assert len(exception.value.validation_errors) == 1
    assert "Path ['id']" in exception.value.validation_errors[0]


def test_given_composite_pk_but_only_one_path_valid_when_get_inferred_schemas_then_valid_path_is_required():
    inferrer = SchemaInferrer([["id 1"], ["id 2"]])
    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"id 1": _ANY_VALUE}, emitted_at=NOW))

    with pytest.raises(SchemaValidationException) as exception:
        inferrer.get_stream_schema(_STREAM_NAME)

    assert exception.value.schema["required"] == ["id 1"]


def test_given_composite_pk_but_only_one_path_valid_when_get_inferred_schemas_then_validation_error_mentions_where_the_issue_is():
    inferrer = SchemaInferrer([["id 1"], ["id 2"]])
    inferrer.accumulate(AirbyteRecordMessage(stream=_STREAM_NAME, data={"id 1": _ANY_VALUE}, emitted_at=NOW))

    with pytest.raises(SchemaValidationException) as exception:
        inferrer.get_stream_schema(_STREAM_NAME)

    assert len(exception.value.validation_errors) == 1
    assert "id 2" in exception.value.validation_errors[0]
