#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader


class JsonSchema(SchemaLoader):
    def __init__(self, file_path: Union[str, InterpolatedString], config, name: str, **kwargs):
        if type(file_path) == str:
            file_path = InterpolatedString(file_path)
        print(f"file_path: {file_path._string}")
        self._file_path = file_path
        self._config = config
        self._kwargs = kwargs
        self._name = name

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema_path = self._file_path.eval(self._config, name=self._name, **self._kwargs)
        print(f"runtime schema path: {json_schema_path}")
        print(f"template: {self._file_path._string}")
        print(f"kwargs: {self._kwargs}")
        print(f"name: {self._name}")
        with open(json_schema_path, "r") as f:
            return json.loads(f.read())
