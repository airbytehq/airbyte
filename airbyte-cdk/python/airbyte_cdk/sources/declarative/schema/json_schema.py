#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


class JsonSchema(SchemaLoader):
    def __init__(self, file_path: InterpolatedString, config, **kwargs):
        self._file_path = file_path
        self._config = config
        self._kwargs = kwargs

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema_path = self._get_json_filepath()
        with open(json_schema_path, "r") as f:
            return json.loads(f.read())

    def _get_json_filepath(self):
        return self._file_path.eval(self._config, **self._kwargs)
