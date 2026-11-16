#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import pkgutil
from dataclasses import dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader


@dataclass
class AdjustSchemaLoader(JsonFileSchemaLoader):
    config: Mapping[str, Any]

    def get_json_schema(self) -> Mapping[str, Any]:
        """Load the frozen pydantic-v1 Report schema."""
        schema = json.loads(pkgutil.get_data("source_adjust", "schemas/report.json"))
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
