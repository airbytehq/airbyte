#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


@dataclass
class CustomFieldsSchemaLoader(SchemaLoader):
    config: Mapping[str, Any]
    default_schema_loader: Optional[SchemaLoader] = None
    fields_config_key: Optional[str] = None
    include_default_fields: Optional[bool] = False
    include_default_fields_config_key: Optional[bool] = False

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Returns the JSON schema.

        The final schema is constructed by first generating a schema for the fields
        in the config and, if default fields should be included, adding these to the
        schema.
        """
        schema = self._get_json_schema_from_config()
        if self.default_schema_loader and self._include_default_fields:
            default_schema = self.default_schema_loader.get_json_schema()
            schema = self._union_schemas(default_schema, schema)
        return schema

    def _include_default_fields(self):
        if self.include_default_fields:
            return True
        else:
            return self.include_default_fields_config_key and self.config.get(self.include_default_fields_config_key, False)

    def _get_json_schema_from_config(self):
        if self.fields_config_key and self.config.get(self.fields_config_key, None):
            properties = {
                field.strip(): {"type": ["null", "string"]}
                for field in self.convert_custom_reports_fields_to_list(self.config.get(self.fields_config_key))
            }
        else:
            properties = {}
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }

    def convert_custom_reports_fields_to_list(self, custom_reports_fields: str) -> list:
        return custom_reports_fields.split(",") if custom_reports_fields else []

    def _union_schemas(self, schema1, schema2):
        schema1["properties"] = {**schema1["properties"], **schema2["properties"]}
        return schema1
