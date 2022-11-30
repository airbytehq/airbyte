#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from airbyte_cdk.sources.utils.schema_models import AllOptional, BaseSchemaModel


class InnerClass(BaseSchemaModel):
    field1: Optional[str]
    field2: int


class SchemaWithFewNullables(BaseSchemaModel):
    name: Optional[str]
    optional_item: Optional[InnerClass]
    items: List[InnerClass]


class SchemaWithAllOptional(BaseSchemaModel, metaclass=AllOptional):
    object_id: int
    item: InnerClass


class TestSchemaWithFewNullables:
    EXPECTED_SCHEMA = {
        "type": "object",
        "properties": {
            "name": {"type": ["null", "string"]},
            "optional_item": {
                "oneOf": [
                    {"type": "null"},
                    {"type": "object", "properties": {"field1": {"type": ["null", "string"]}, "field2": {"type": "integer"}}},
                ]
            },
            "items": {
                "type": "array",
                "items": {"type": "object", "properties": {"field1": {"type": ["null", "string"]}, "field2": {"type": "integer"}}},
            },
        },
    }

    def test_schema_postprocessing(self):
        schema = SchemaWithFewNullables.schema()
        assert schema == self.EXPECTED_SCHEMA


class TestSchemaWithAllOptional:
    EXPECTED_SCHEMA = {
        "type": "object",
        "properties": {
            "object_id": {"type": ["null", "integer"]},
            "item": {
                "oneOf": [
                    {"type": "null"},
                    {"type": "object", "properties": {"field1": {"type": ["null", "string"]}, "field2": {"type": "integer"}}},
                ]
            },
        },
    }

    def test_schema_postprocessing(self):
        schema = SchemaWithAllOptional.schema()
        assert schema == self.EXPECTED_SCHEMA
