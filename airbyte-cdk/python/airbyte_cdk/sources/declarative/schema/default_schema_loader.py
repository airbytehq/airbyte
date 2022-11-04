#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DefaultSchemaLoader(SchemaLoader, JsonSchemaMixin):
    """
    Loads a schema from the default location or returns an empty schema for streams that have not defined their schema file yet.

    Attributes:
        config (Config): The user-provided configuration as specified by the source's spec
        options (Mapping[str, Any]): Additional arguments to pass to the string interpolation if needed
    """

    config: Config
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self.default_loader = JsonFileSchemaLoader(options=options, config=self.config)

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Attempts to retrieve a schema from the default filepath location or returns the empty schema if a schema cannot be found.

        :return: The empty schema
        """

        try:
            return self.default_loader.get_json_schema()
        except FileNotFoundError:
            return {}
