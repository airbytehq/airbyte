#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.types import Config


@dataclass
class DefaultSchemaLoader(SchemaLoader):
    """
    Loads a schema from the default location or returns an empty schema for streams that have not defined their schema file yet.

    Attributes:
        config (Config): The user-provided configuration as specified by the source's spec
        parameters (Mapping[str, Any]): Additional arguments to pass to the string interpolation if needed
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        self.default_loader = JsonFileSchemaLoader(parameters=parameters, config=self.config)

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Attempts to retrieve a schema from the default filepath location or returns the empty schema if a schema cannot be found.

        :return: The empty schema
        """

        try:
            return self.default_loader.get_json_schema()
        except (OSError, ValueError):
            # A slight hack since we don't directly have the stream name. However, when building the default filepath we assume the
            # runtime options stores stream name 'name' so we'll do the same here
            stream_name = self._parameters.get("name", "")
            logging.info(
                f"Could not find schema for stream {stream_name}, defaulting to the empty schema"
            )
            return {}
