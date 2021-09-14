#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import os
import pkgutil
from typing import Any, ClassVar, Dict, Mapping, Tuple

import pkg_resources
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from jsonschema import RefResolver, validate
from jsonschema.exceptions import ValidationError
from pydantic import BaseModel, Field


class JsonSchemaResolver:
    """Helper class to expand $ref items in json schema"""

    def __init__(self, shared_schemas_path: str):
        self._shared_refs = self._load_shared_schema_refs(shared_schemas_path)

    @staticmethod
    def _load_shared_schema_refs(shared_schemas_path: str):
        shared_file_names = [f.name for f in os.scandir(shared_schemas_path) if f.is_file()]
        shared_schema_refs = {}
        for shared_file in shared_file_names:
            with open(os.path.join(shared_schemas_path, shared_file)) as data_file:
                shared_schema_refs[shared_file] = json.load(data_file)

        return shared_schema_refs

    def _resolve_schema_references(self, schema: dict, resolver: RefResolver) -> dict:
        if "$ref" in schema:
            reference_path = schema.pop("$ref", None)
            resolved = resolver.resolve(reference_path)[1]
            schema.update(resolved)
            return self._resolve_schema_references(schema, resolver)

        if "properties" in schema:
            for k, val in schema["properties"].items():
                schema["properties"][k] = self._resolve_schema_references(val, resolver)

        if "patternProperties" in schema:
            for k, val in schema["patternProperties"].items():
                schema["patternProperties"][k] = self._resolve_schema_references(val, resolver)

        if "items" in schema:
            schema["items"] = self._resolve_schema_references(schema["items"], resolver)

        if "anyOf" in schema:
            for i, element in enumerate(schema["anyOf"]):
                schema["anyOf"][i] = self._resolve_schema_references(element, resolver)

        return schema

    def resolve(self, schema: dict, refs: Dict[str, dict] = None) -> dict:
        """Resolves and replaces json-schema $refs with the appropriate dict.
        Recursively walks the given schema dict, converting every instance
        of $ref in a 'properties' structure with a resolved dict.
        This modifies the input schema and also returns it.
        Arguments:
            schema:
                the schema dict
            refs:
                a dict of <string, dict> which forms a store of referenced schemata
        Returns:
            schema
        """
        refs = refs or {}
        refs = {**self._shared_refs, **refs}
        return self._resolve_schema_references(schema, RefResolver("", schema, store=refs))


class ResourceSchemaLoader:
    """JSONSchema loader from package resources"""

    def __init__(self, package_name: str):
        self.package_name = package_name

    def get_schema(self, name: str) -> dict:
        """
        This method retrieves a JSON schema from the schemas/ folder.


        The expected file structure is to have all top-level schemas (corresponding to streams) in the "schemas/" folder, with any shared $refs
        living inside the "schemas/shared/" folder. For example:

        schemas/shared/<shared_definition>.json
        schemas/<name>.json # contains a $ref to shared_definition
        schemas/<name2>.json # contains a $ref to shared_definition
        """

        schema_filename = f"schemas/{name}.json"
        raw_file = pkgutil.get_data(self.package_name, schema_filename)
        if not raw_file:
            raise IOError(f"Cannot find file {schema_filename}")
        try:
            raw_schema = json.loads(raw_file)
        except ValueError:
            # TODO use proper logging
            print(f"Invalid JSON file format for file {schema_filename}")
            raise

        shared_schemas_folder = pkg_resources.resource_filename(self.package_name, "schemas/shared/")
        if os.path.exists(shared_schemas_folder):
            return JsonSchemaResolver(shared_schemas_folder).resolve(raw_schema)
        return raw_schema


def check_config_against_spec_or_exit(config: Mapping[str, Any], spec: ConnectorSpecification, logger: AirbyteLogger):
    """
    Check config object against spec. In case of spec is invalid, throws
    an exception with validation error description.
    :param config - config loaded from file specified over command line
    :param spec - spec object generated by connector
    :param logger - Airbyte logger for reporting validation error
    """
    spec_schema = spec.connectionSpecification
    try:
        validate(instance=config, schema=spec_schema)
    except ValidationError as validation_error:
        raise Exception("Config validation error: " + validation_error.message) from None


class InternalConfig(BaseModel):
    KEYWORDS: ClassVar[set] = {"_limit", "_page_size"}
    limit: int = Field(None, alias="_limit")
    page_size: int = Field(None, alias="_page_size")

    def dict(self):
        return super().dict(by_alias=True, exclude_unset=True)


def split_config(config: Mapping[str, Any]) -> Tuple[dict, InternalConfig]:
    """
    Break config map object into 2 instances: first is a dict with user defined
    configuration and second is internal config that contains private keys for
    acceptance test configuration.
    :param
     config - Dict object that has been loaded from config file.
    :return tuple of user defined config dict with filtered out internal
    parameters and SAT internal config object.
    """
    main_config = {}
    internal_config = {}
    for k, v in config.items():
        if k in InternalConfig.KEYWORDS:
            internal_config[k] = v
        else:
            main_config[k] = v
    return main_config, InternalConfig.parse_obj(internal_config)
