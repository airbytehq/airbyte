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


import importlib
import json
import os
import pkgutil
from typing import Any, ClassVar, Dict, Mapping, Tuple

import jsonref
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from pydantic import BaseModel, Field


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

        return self.__resolve_schema_references(raw_schema)

    def __resolve_schema_references(self, raw_schema: dict) -> dict:
        """
        Resolve links to external references and move it to local "definitions" map.
        :param raw_schema jsonschema to lookup for external links.
        :return JSON serializable object with references without external dependencies.
        """

        class JsonFileLoader:
            """
            Custom json file loader to resolve references to resources located in "shared" directory.
            We need this for compatability with existing schemas cause all of them have references
            pointing to shared_schema.json file instead of shared/shared_schema.json
            """

            def __init__(self, uri_base: str, shared: str):
                self.shared = shared
                self.uri_base = uri_base

            def __call__(self, uri: str) -> Dict[str, Any]:
                uri = uri.replace(self.uri_base, f"{self.uri_base}/{self.shared}/")
                return json.load(open(uri))

        package = importlib.import_module(self.package_name)
        base = os.path.dirname(package.__file__) + "/"

        def create_definitions(obj: dict, definitions: dict) -> Dict[str, Any]:
            """
            Scan resolved schema and compose definitions section, also convert
            jsonref.JsonRef object to JSON serializable dict.
            :param obj - jsonschema object with ref field resovled.
            :definitions - object for storing generated definitions.
            :return JSON serializable object with references without external dependencies.
            """
            if isinstance(obj, jsonref.JsonRef):
                def_key = obj.__reference__["$ref"]
                def_key = def_key.replace("#/definitions/", "").replace(".json", "_")
                definition = create_definitions(obj.__subject__, definitions)
                # Omit existance definitions for extenal resource since
                # we dont need it anymore.
                definition.pop("definitions", None)
                definitions[def_key] = definition
                return {"$ref": "#/definitions/" + def_key}
            elif isinstance(obj, dict):
                return {k: create_definitions(v, definitions) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [create_definitions(item, definitions) for item in obj]
            else:
                return obj

        resolved = jsonref.JsonRef.replace_refs(raw_schema, loader=JsonFileLoader(base, "schemas/shared"), base_uri=base)
        definitions = {}
        resolved = create_definitions(resolved, definitions)
        if definitions:
            resolved["definitions"] = definitions
        return resolved


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
