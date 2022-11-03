#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class EmptySchemaLoader(SchemaLoader, JsonSchemaMixin):
    """
    Loads an empty schema for streams that have not defined their schema file yet.

    Attributes:
        config (Config): The user-provided configuration as specified by the source's spec
        options (Mapping[str, Any]): Additional arguments to pass to the string interpolation if needed
    """

    config: Config
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        pass

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Returns by default the empty schema.

        :return: The empty schema
        """

        return {}
