#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class JsonSchema(SchemaLoader, JsonSchemaMixin):
    """
    Loads the schema from a json file

    Attributes:
        file_path (Union[InterpolatedString, str]): The path to the json file describing the schema
        name (str): The stream's name
        config (Config): The user-provided configuration as specified by the source's spec
        options (Mapping[str, Any]): Additional arguments to pass to the string interpolation if needed
    """

    file_path: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self.file_path = InterpolatedString.create(self.file_path, options=options)

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema_path = self._get_json_filepath()
        with open(json_schema_path, "r") as f:
            return json.loads(f.read())

    def _get_json_filepath(self):
        return self.file_path.eval(self.config)
