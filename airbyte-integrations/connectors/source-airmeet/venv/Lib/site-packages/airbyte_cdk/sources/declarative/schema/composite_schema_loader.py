#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Dict, List, Mapping

from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


@dataclass
class CompositeSchemaLoader(SchemaLoader):
    """
    Schema loader that consists of multiple schema loaders that are combined into a single
    schema. Subsequent schemas do not overwrite existing values so the schema loaders with
    a higher priority should be defined first.
    """

    schema_loaders: List[SchemaLoader]
    parameters: InitVar[Mapping[str, Any]]

    def get_json_schema(self) -> Mapping[str, Any]:
        combined_schema: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "properties": {},
        }
        for schema_loader in self.schema_loaders:
            schema_properties = schema_loader.get_json_schema()["properties"]
            combined_schema["properties"] = {**schema_properties, **combined_schema["properties"]}
        return combined_schema
