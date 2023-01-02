#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer

NOW = 1234567


def test_deriving_schema():
    inferrer = SchemaInferrer()
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"id": 0, "field_A": 1.0, "field_B": "airbyte"}, emitted_at=NOW))
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"id": 1, "field_A": 2.0, "field_B": "abc"}, emitted_at=NOW))
    assert json.dumps(inferrer.get_inferred_schemas()["my_stream"]) == '{"$schema": "http://json-schema.org/schema#", "type": "object", "properties": {"id": {"type": "integer"}, "field_A": {"type": "number"}, "field_B": {"type": "string"}}}'


def test_deriving_schema_refine():
    inferrer = SchemaInferrer()
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"field_A": 1.0}, emitted_at=NOW))
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"field_A": "abc"}, emitted_at=NOW))
    assert json.dumps(inferrer.get_inferred_schemas()["my_stream"]) == '{"$schema": "http://json-schema.org/schema#", "type": "object", "properties": {"field_A": {"type": ["number", "string"]}}}'


def test_deriving_schema_multiple_streams():
    inferrer = SchemaInferrer()
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"field_A": 1.0}, emitted_at=NOW))
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream2", data={"field_A": "abc"}, emitted_at=NOW))
    inferred_schemas = inferrer.get_inferred_schemas()
    assert json.dumps(inferred_schemas["my_stream"]) == '{"$schema": "http://json-schema.org/schema#", "type": "object", "properties": {"field_A": {"type": "number"}}}'
    assert json.dumps(inferred_schemas["my_stream2"]) == '{"$schema": "http://json-schema.org/schema#", "type": "object", "properties": {"field_A": {"type": "string"}}}'


def test_get_individual_schema():
    inferrer = SchemaInferrer()
    inferrer.accumulate(AirbyteRecordMessage(stream="my_stream", data={"field_A": 1.0}, emitted_at=NOW))
    assert json.dumps(inferrer.get_stream_schema("my_stream")) == '{"$schema": "http://json-schema.org/schema#", "type": "object", "properties": {"field_A": {"type": "number"}}}'
    assert inferrer.get_stream_schema("another_stream") is None
