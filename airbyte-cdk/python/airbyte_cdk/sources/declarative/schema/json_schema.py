#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import pkgutil
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
        resource, schema_path = self.extract_resource_and_schema_path(json_schema_path)
        json_schema = pkgutil.get_data(resource, schema_path)

        if not json_schema:
            raise FileNotFoundError("File not found: " + json_schema_path)
        return json.loads(json_schema)

    def _get_json_filepath(self):
        return self.file_path.eval(self.config)

    @staticmethod
    def extract_resource_and_schema_path(json_schema_path: str) -> (str, str):
        """
        When the connector is running on a docker container, package_data is accessible from the resource (source_<name>), so we extract
        the resource from the first part of the schema path and the remaining path is used to find the schema file. This is a slight
        hack to identify the source name while we are in the airbyte_cdk module.
        :param json_schema_path: The path to the schema JSON file
        :return: Tuple of the resource name and the path to the schema file
        """
        split_path = json_schema_path.split("/")

        if split_path[0] == "" or split_path[0] == ".":
            split_path = split_path[1:]

        if len(split_path) == 0:
            return "", ""

        if len(split_path) == 1:
            return "", split_path[0]

        return split_path[0], "/".join(split_path[1:])
