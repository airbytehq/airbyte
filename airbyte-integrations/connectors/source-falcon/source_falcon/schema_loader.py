# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from source_falcon.schema_helper import ReportXMLSchemaHelper

from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader


class ReportSchemaLoader(DefaultSchemaLoader):
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        self.default_loader = ReportXMLSchemaHelper(self.config, self._parameters["report_id"])
        self.schema = {}

    def get_json_schema(self) -> Mapping[str, Any]:
        if not self.schema:
            self.schema = {
                "$schema": "https://json-schema.org/draft-04/schema#",
                "type": "object",
                "properties": self.default_loader.get_properties(),
                "additionalProperties": True,
            }

        return self.schema
