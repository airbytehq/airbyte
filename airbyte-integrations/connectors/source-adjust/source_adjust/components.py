#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping

import source_adjust.model
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader


@dataclass
class AdjustSchemaLoader(JsonFileSchemaLoader):

    config: Mapping[str, Any]

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Prune the schema to only include selected fields to synchronize.
        """
        schema = source_adjust.model.Report.schema()
        properties = schema["properties"]

        required = schema["required"]
        selected = self.config["metrics"] + self.config["dimensions"]
        retain = required + selected
        for attr in list(properties.keys()):
            if attr not in retain:
                del properties[attr]

        for attr in self.config["additional_metrics"]:
            properties[attr] = {"type": "number"}

        return schema
