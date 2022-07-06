#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from pydantic import BaseModel


class JsonSchema(SchemaLoader, BaseModel):
    file_path: InterpolatedString
    config: dict
    kwargs: dict

    def get_json_schema(self) -> Mapping[str, Any]:
        with open(self.file_path.eval(self.config, **self.kwargs), "r") as f:
            return json.loads(f.read())
