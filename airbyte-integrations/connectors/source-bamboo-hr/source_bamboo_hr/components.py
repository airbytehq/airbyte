#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader, _default_file_path


@dataclass
class BambooHRSchemaLoader(JsonFileSchemaLoader):

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]] = {"name": "custom_reports_stream"}

    def __post_init__(self, parameters: Mapping[str, Any]):
        if not self.file_path:
            self.file_path = _default_file_path()
        self.file_path = InterpolatedString.create(self.file_path, parameters=self.parameters)

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Returns the JSON schema.

        The final schema is constructed by first generating a schema for the fields
        in the config and, if default fields should be included, adding these to the
        schema.
        """
        schema = self._get_json_schema_from_config()
        if self.config.get("custom_reports_include_default_fields"):
            default_schema = self._get_json_schema_from_file()
            schema = self._union_schemas(default_schema, schema)
        return schema

    def _get_json_schema_from_config(self):
        if self.config.get("custom_reports_fields"):
            properties = {
                field.strip(): {"type": ["null", "string"]}
                for field in self.convert_custom_reports_fields_to_list(self.config.get("custom_reports_fields", ""))
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

    def _get_json_schema_from_file(self):
        return super().get_json_schema()

    def _union_schemas(self, schema1, schema2):
        schema1["properties"] = {**schema1["properties"], **schema2["properties"]}
        return schema1
