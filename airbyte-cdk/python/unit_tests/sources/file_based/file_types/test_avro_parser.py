#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.file_types import AvroParser

_default_avro_format = AvroFormat()
_decimal_as_float_avro_format = AvroFormat(decimal_as_float=True)


@pytest.mark.parametrize(
    "avro_format, avro_type, expected_json_type, expected_error",
    [
        # Primitive types
        pytest.param(_default_avro_format, "null", {"type": "null"}, None, id="test_null"),
        pytest.param(_default_avro_format, "boolean", {"type": "boolean"}, None, id="test_boolean"),
        pytest.param(_default_avro_format, "int", {"type": "integer"}, None, id="test_int"),
        pytest.param(_default_avro_format, "long", {"type": "integer"}, None, id="test_long"),
        pytest.param(_default_avro_format, "float", {"type": "number"}, None, id="test_float"),
        pytest.param(_default_avro_format, "double", {"type": "string"}, None, id="test_double"),
        pytest.param(_decimal_as_float_avro_format, "double", {"type": "number"}, None, id="test_double_as_float"),
        pytest.param(_default_avro_format, "bytes", {"type": "string"}, None, id="test_bytes"),
        pytest.param(_default_avro_format, "string", {"type": "string"}, None, id="test_string"),
        pytest.param(_default_avro_format, "void", None, ValueError, id="test_invalid_type"),
        # Complex types
        pytest.param(
            _default_avro_format,
            {
                "type": "record",
                "name": "SubRecord",
                "fields": [{"name": "precise", "type": "double"}, {"name": "robo", "type": "bytes"}, {"name": "simple", "type": "long"}],
            },
            {
                "type": "object",
                "properties": {
                    "precise": {"type": "string"},
                    "robo": {"type": "string"},
                    "simple": {"type": "integer"},
                },
            },
            None,
            id="test_record",
        ),
        pytest.param(
            _default_avro_format,
            {
                "type": "record",
                "name": "SubRecord",
                "fields": [{"name": "precise", "type": "double"}, {"name": "obj_array", "type": {"type": "array", "items": "float"}}],
            },
            {"type": "object", "properties": {"precise": {"type": "string"}, "obj_array": {"type": "array", "items": {"type": "number"}}}},
            None,
            id="test_record_with_nested_array",
        ),
        pytest.param(
            _default_avro_format,
            {
                "type": "record",
                "name": "SubRecord",
                "fields": [
                    {
                        "name": "nested_record",
                        "type": {"type": "record", "name": "SubRecord", "fields": [{"name": "question", "type": "boolean"}]},
                    }
                ],
            },
            {
                "type": "object",
                "properties": {
                    "nested_record": {
                        "type": "object",
                        "properties": {"question": {"type": "boolean"}},
                    }
                },
            },
            None,
            id="test_record_with_nested_record",
        ),
        pytest.param(_default_avro_format, {"type": "array", "items": "float"}, {"type": "array", "items": {"type": "number"}}, None,
                     id="test_array"),
        pytest.param(
            _default_avro_format,
            {"type": "array", "items": {"type": "record", "name": "SubRecord", "fields": [{"name": "precise", "type": "double"}]}},
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "precise": {"type": "string"},
                    },
                },
            },
            None,
            id="test_array_of_records",
        ),
        pytest.param(_default_avro_format, {"type": "array", "not_items": "string"}, None, ValueError, id="test_array_missing_items"),
        pytest.param(_default_avro_format, {"type": "array", "items": "invalid_avro_type"}, None, ValueError,
                     id="test_array_invalid_item_type"),
        pytest.param(
            _default_avro_format,
            {"type": "enum", "name": "IMF", "symbols": ["Ethan", "Benji", "Luther"]},
            {"type": "string", "enum": ["Ethan", "Benji", "Luther"]},
            None,
            id="test_enum",
        ),
        pytest.param(_default_avro_format, {"type": "enum", "name": "IMF"}, None, ValueError, id="test_enum_missing_symbols"),
        pytest.param(_default_avro_format, {"type": "enum", "symbols": ["mission", "not", "accepted"]}, None, ValueError,
                     id="test_enum_missing_name"),
        pytest.param(
            _default_avro_format,
            {"type": "map", "values": "int"}, {"type": "object", "additionalProperties": {"type": "integer"}}, None, id="test_map"
        ),
        pytest.param(
            _default_avro_format,
            {"type": "map", "values": {"type": "record", "name": "SubRecord", "fields": [{"name": "agent", "type": "string"}]}},
            {"type": "object", "additionalProperties": {"type": "object", "properties": {"agent": {"type": "string"}}}},
            None,
            id="test_map_object",
        ),
        pytest.param(_default_avro_format, {"type": "map"}, None, ValueError, id="test_map_missing_values"),
        pytest.param(
            _default_avro_format,
            {"type": "fixed", "name": "limit", "size": 12}, {"type": "string", "pattern": "^[0-9A-Fa-f]{24}$"}, None, id="test_fixed"
        ),
        pytest.param(_default_avro_format, {"type": "fixed", "name": "limit"}, None, ValueError, id="test_fixed_missing_size"),
        pytest.param(_default_avro_format, {"type": "fixed", "name": "limit", "size": "50"}, None, ValueError,
                     id="test_fixed_size_not_integer"),
        # Logical types
        pytest.param(
            _default_avro_format,
            {"type": "bytes", "logicalType": "decimal", "precision": 9, "scale": 4},
            {"type": "string", "pattern": f"^-?\\d{{{1, 5}}}(?:\\.\\d{1, 4})?$"},
            None,
            id="test_decimal",
        ),
        pytest.param(_default_avro_format, {"type": "bytes", "logicalType": "decimal", "scale": 4}, None, ValueError,
                     id="test_decimal_missing_precision"),
        pytest.param(_default_avro_format, {"type": "bytes", "logicalType": "decimal", "precision": 9}, None, ValueError,
                     id="test_decimal_missing_scale"),
        pytest.param(_default_avro_format, {"type": "bytes", "logicalType": "uuid"}, {"type": ["null", "string"]}, None, id="test_uuid"),
        pytest.param(_default_avro_format, {"type": "int", "logicalType": "date"}, {"type": ["null", "string"], "format": "date"}, None,
                     id="test_date"),
        pytest.param(_default_avro_format, {"type": "int", "logicalType": "time-millis"}, {"type": ["null", "integer"]}, None, id="test_time_millis"),
        pytest.param(_default_avro_format, {"type": "long", "logicalType": "time-micros"}, {"type": ["null", "integer"]}, None,
                     id="test_time_micros"),
        pytest.param(
            _default_avro_format,
            {"type": "long", "logicalType": "timestamp-millis"}, {"type": ["null", "string"], "format": "date-time"}, None, id="test_timestamp_millis"
        ),
        pytest.param(_default_avro_format, {"type": "long", "logicalType": "timestamp-micros"}, {"type": ["null", "string"]}, None,
                     id="test_timestamp_micros"),
        pytest.param(
            _default_avro_format,
            {"type": "long", "logicalType": "local-timestamp-millis"}, {"type": "string", "format": "date-time"}, None,
            id="test_local_timestamp_millis"
        ),
        pytest.param(_default_avro_format, {"type": "long", "logicalType": "local-timestamp-micros"}, {"type": "string"}, None,
                     id="test_local_timestamp_micros"),

    ],
)
def test_convert_primitive_avro_type_to_json(avro_format, avro_type, expected_json_type, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            AvroParser._convert_avro_type_to_json(avro_format, "field_name", avro_type)
    else:
        actual_json_type = AvroParser._convert_avro_type_to_json(avro_format, "field_name", avro_type)
        assert actual_json_type == expected_json_type
