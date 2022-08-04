#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config


class JsonSchema(SchemaLoader):
    """Loads the schema from a json file"""

    def __init__(self, file_path: InterpolatedString, config: Config, **options: Optional[Mapping[str, Any]]):
        """
        :param file_path: The path to the json file describing the schema
        :param config: The user-provided configuration as specified by the source's spec
        :param options: Additional arguments to pass to the string interpolation if needed
        """
        self._file_path = file_path
        self._config = config
        self._options = options

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema_path = self._get_json_filepath()
        with open(json_schema_path, "r") as f:
            return json.loads(f.read())

    def _get_json_filepath(self):
        return self._file_path.eval(self._config, **self._options)
