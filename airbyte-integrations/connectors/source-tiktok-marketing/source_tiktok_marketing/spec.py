#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import re
from copy import deepcopy
from typing import Union

from jsonschema import RefResolver
from pydantic import BaseModel, Field

# TikTok Initial release date is September 2016
DEFAULT_START_DATE = "01-09-2016"


class SandboxEnvSpec(BaseModel):
    class Config:
        title = "Sandbox"

    environment: str = Field("sandbox", const=True)

    # it is string because UI has the bug https://github.com/airbytehq/airbyte/issues/6875
    advertiser_id: str = Field(
        description="The Advertiser ID  which generated for the developer's Sandbox application.",
    )


class ProductionEnvSpec(BaseModel):
    class Config:
        title = "Production"

    environment: str = Field("prod", const=True)

    # it is float because UI has the bug https://github.com/airbytehq/airbyte/issues/6875
    app_id: str = Field(
        description="The App id applied by the developer.",
    )
    secret: str = Field(description="The private key of the developer's application.", airbyte_secret=True)


class SourceTiktokMarketingSpec(BaseModel):
    class Config:
        title = "TikTok Marketing Source Spec"

    environment: Union[ProductionEnvSpec, SandboxEnvSpec] = Field(default=ProductionEnvSpec.Config.title)

    access_token: str = Field(description="Long-term Authorized Access Token.", airbyte_secret=True)

    start_date: str = Field(
        description="Start Date in format: YYYY-MM-DD.", default=DEFAULT_START_DATE, pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    )

    @staticmethod
    def change_format_to_oneOf(schema: dict, field_name: str) -> dict:
        schema["properties"][field_name]["oneOf"] = deepcopy(schema["properties"][field_name]["anyOf"])
        schema["properties"][field_name]["type"] = "object"
        del schema["properties"][field_name]["anyOf"]
        return schema

    @staticmethod
    def resolve_refs(schema: dict) -> dict:
        json_schema_ref_resolver = RefResolver.from_schema(schema)
        str_schema = json.dumps(schema)
        for ref_block in re.findall(r'{"\$ref": "#\/definitions\/.+?(?="})"}', str_schema):
            ref = json.loads(ref_block)["$ref"]
            str_schema = str_schema.replace(ref_block, json.dumps(json_schema_ref_resolver.resolve(ref)[1]))
        pyschema = json.loads(str_schema)
        del pyschema["definitions"]
        return pyschema

    @classmethod
    def schema(cls) -> dict:
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = cls.change_format_to_oneOf(schema, "environment")
        return cls.resolve_refs(schema)
