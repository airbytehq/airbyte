#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class JsonSchema(SchemaLoader, JsonSchemaMixin):
    """JsonSchema"""

    file_path: Union[InterpolatedString, str]
    name: str
    config: Config = field(default_factory=dict)
    kwargs: dict = field(default_factory=dict)

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema_path = self._get_json_filepath()
        with open(json_schema_path, "r") as f:
            return json.loads(f.read())

    def _get_json_filepath(self):
        print(f"get json filepath with name={self.name} and file_path={self.file_path}")
        eval = self.file_path.eval(self.config, name=self.name, **self.kwargs)
        print(f"eval: {eval}")
        return eval
