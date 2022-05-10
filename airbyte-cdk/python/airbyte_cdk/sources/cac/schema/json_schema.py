#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
import os
from typing import Any, Mapping

from airbyte_cdk.sources.cac.schema.schema_loader import SchemaLoader


class JsonSchema(SchemaLoader):
    def __init__(self, file_path, vars=None, config=None):
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        # Small hack until i figure out the docker issue
        if not os.path.exists(file_path):
            relative = "/".join(file_path.split("/")[-3:])
            file_path = f"/airbyte/integration_code/{relative}"

        self._file_path = file_path
        self._vars = vars
        self._config = config

    def get_json_schema(self) -> Mapping[str, Any]:
        with open(self._file_path, "r") as f:
            return json.loads(f.read())
