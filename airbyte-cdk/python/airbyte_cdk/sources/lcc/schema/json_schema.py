#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
from typing import Any, Mapping

from airbyte_cdk.sources.lcc.schema.schema_loader import SchemaLoader


class JsonSchema(SchemaLoader):
    def __init__(self, file_path):
        self._file_path = file_path

    def get_json_schema(self) -> Mapping[str, Any]:
        with open(self._file_path, "r") as f:
            return json.loads(f.read())
