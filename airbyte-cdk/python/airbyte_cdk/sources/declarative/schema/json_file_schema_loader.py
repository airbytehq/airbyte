#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import importlib
import json
import os
import pkgutil
import sys
from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Union, Dict, List

import jsonref
from dataclasses_jsonschema import JsonSchemaMixin

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.utils.schema_helpers import JsonFileLoader


def _default_file_path() -> str:
    # Schema files are always in "source_<connector_name>/schemas/<stream_name>.json
    # The connector's module name can be inferred by looking at the modules loaded and look for the one starting with source_
    source_modules = [
        k for k, v in sys.modules.items() if "source_" in k
    ]  # example: ['source_exchange_rates', 'source_exchange_rates.source']
    if source_modules:
        module = source_modules[0].split(".")[0]
        return f"./{module}/schemas/{{{{options['name']}}}}.json"

    # If we are not in a source_ module, the most likely scenario is we're processing a manifest from the connector builder
    # server which does not require a json schema to be defined.
    return "./{{options['name']}}.json"


@dataclass
class JsonFileSchemaLoader(SchemaLoader, JsonSchemaMixin):
    """
    Loads the schema from a json file

    Attributes:
        file_path (Union[InterpolatedString, str]): The path to the json file describing the schema
        name (str): The stream's name
        config (Config): The user-provided configuration as specified by the source's spec
        options (Mapping[str, Any]): Additional arguments to pass to the string interpolation if needed
    """

    config: Config
    options: InitVar[Mapping[str, Any]]
    file_path: Union[InterpolatedString, str] = field(default=None)
    __resource: str = None

    def __post_init__(self, options: Mapping[str, Any]):
        if not self.file_path:
            self.file_path = _default_file_path()
        self.file_path = InterpolatedString.create(self.file_path, options=options)

    def get_json_schema(self) -> Mapping[str, Any]:
        # todo: It is worth revisiting if we can replace file_path with just file_name if every schema is in the /schemas directory
        # this would require that we find a creative solution to store or retrieve source_name in here since the files are mounted there
        json_schema_path = self._get_json_filepath()
        resource, schema_path = self.extract_resource_and_schema_path(json_schema_path)
        raw_json_file = pkgutil.get_data(resource, schema_path)

        if not raw_json_file:
            raise IOError(f"Cannot find file {json_schema_path}")
        try:
            raw_schema = json.loads(raw_json_file)
        except ValueError as err:
            raise RuntimeError(f"Invalid JSON file format for file {json_schema_path}") from err
        self.__resource = resource
        return self.__resolve_schema_references(raw_schema)

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

    def __resolve_schema_references(self, raw_schema: dict) -> dict:
        """
        Resolve links to external references and move it to local "definitions" map.

        :param raw_schema jsonschema to lookup for external links.
        :return JSON serializable object with references without external dependencies.
        """

        package = importlib.import_module(self.__resource)
        base = os.path.dirname(package.__file__) + "/"
        resolved = jsonref.JsonRef.replace_refs(raw_schema, loader=JsonFileLoader(base, "schemas/shared"), base_uri=base)
        resolved = resolve_ref_links(resolved)
        return resolved


def resolve_ref_links(obj: Any) -> Union[Dict[str, Any], List[Any]]:
    """
    Scan resolved schema and convert jsonref.JsonRef object to JSON serializable dict.

    :param obj - jsonschema object with ref field resolved.
    :return JSON serializable object with references without external dependencies.
    """
    if isinstance(obj, jsonref.JsonRef):
        obj = resolve_ref_links(obj.__subject__)
        # Omit existing definitions for external resource since
        # we do not need it anymore.
        obj.pop("definitions", None)
        return obj
    elif isinstance(obj, dict):
        return {k: resolve_ref_links(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_ref_links(item) for item in obj]
    else:
        return obj
