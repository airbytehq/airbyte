#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from airbyte_cdk.sources.utils.schema_models import BaseSchemaModel


class InnerClass(BaseSchemaModel):
    field1: Optional[str] = None
    field2: int


class SchemaWithFewNullables(BaseSchemaModel):
    name: Optional[str] = None
    optional_item: Optional[InnerClass] = None
    items: List[InnerClass]


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
