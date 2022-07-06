#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from pydantic import BaseModel, validator


class JsonSchema(SchemaLoader, BaseModel):
    file_path: str
    config: dict
    kwargs: Optional[dict] = None

    def get_json_schema(self) -> Mapping[str, Any]:
        with open(self.file_path.eval(self.config, **self.kwargs), "r") as f:
            return json.loads(f.read())

    @validator("file_path")
    def to_interpolated_string(cls, v):
        if isinstance(v, str):
            return InterpolatedString(string=v)
        elif isinstance(v, InterpolatedString):
            return v
        else:
            raise TypeError(f"Expected type str or InterpolatedString for {v}. Got : {type(v)}")
