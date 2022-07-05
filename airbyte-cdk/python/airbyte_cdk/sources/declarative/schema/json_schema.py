#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


class JsonSchema(SchemaLoader):
    def __init__(self, file_path: Union[str, InterpolatedString], config, **kwargs):
        if type(file_path) == str:
            file_path = InterpolatedString(file_path)
        self._file_path = file_path
        self._config = config
        self._kwargs = kwargs

    def get_json_schema(self) -> Mapping[str, Any]:
        with open(self._file_path.eval(self._config, **self._kwargs), "r") as f:
            return json.loads(f.read())
