#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import re
from typing import Union

from jsonschema import RefResolver
from pydantic import BaseModel, Field

from .streams import DEFAULT_START_DATE, ReportGranularity


class OauthCredSpec(BaseModel):
    class Config:
        title = "OAuth authentication"

    auth_type: str = Field(default="Oauth", const=True, order=0, enum=["Oauth"])

    app_id: str = Field(
        title="App ID",
        description="The App id applied by the developer.",
        airbyte_secret=True
    )

    secret: str = Field(
        title="Secret",
        description="The private key of the developer's application.",
        airbyte_secret=True,
    )

    access_token: str = Field(
        title="Access Token",
        description="Long-term Authorized Access Token.",
        airbyte_secret=True
    )

    # it is string because UI has the bug https://github.com/airbytehq/airbyte/issues/6875
    advertiser_id: str = Field(
        title="Advertiser ID",
        description="The Advertiser ID  which generated for the developer's Sandbox application."
    )


class SandboxEnvSpec(BaseModel):
    class Config:
        title = "Sandbox"

    environment: str = Field("sandbox", const=True)

    # it is string because UI has the bug https://github.com/airbytehq/airbyte/issues/6875
    advertiser_id: str = Field(
        title="Advertiser ID",
        description="The Advertiser ID  which generated for the developer's Sandbox application.",
    )


class ProductionEnvSpec(BaseModel):
    class Config:
        title = "Production"

    environment: str = Field("prod", const=True)

    # it is float because UI has the bug https://github.com/airbytehq/airbyte/issues/6875
    app_id: str = Field(
        description="The App ID applied by the developer.",
        title="App ID",
        description="The App id applied by the developer."
    )
    secret: str = Field(
        title="Secret",
        description="The private key of the developer application.",
        airbyte_secret=True,
    )


class AccessTokenCredSpec(BaseModel):
    class Config:
        title = "Access token authentication"

    auth_type: str = Field(default="Access token", const=True, order=1, enum=["Access token"])

    environment: Union[ProductionEnvSpec, SandboxEnvSpec] = Field(default=ProductionEnvSpec.Config.title)

    access_token: str = Field(
        title="Access Token",
        description="The Long-term Authorized Access Token.",
        airbyte_secret=True
    )

class SourceTiktokMarketingSpec(BaseModel):
    class Config:
        title = "TikTok Marketing Source Spec"

    credentials: Union[OauthCredSpec, AccessTokenCredSpec] = Field(title="Authorization Method")

    start_date: str = Field(
        title="Start Date",
        description="Start Date in format: YYYY-MM-DD.",
        default=DEFAULT_START_DATE,
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        description="The Start Date in format: YYYY-MM-DD. Any data before this date will not be replicated. If this parameter is not set, all data will be replicated.",
        default=DEFAULT_START_DATE,
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
    )

    report_granularity: str = Field(
        title="Report Granularity",
        description="Which time granularity should be grouped by; for LIFETIME there will be no grouping. "
        "This option is used for reports' streams only.",
        default=ReportGranularity.default().value,
        enum=[g.value for g in ReportGranularity],
    )

    @staticmethod
    def change_format_to_oneOf(schema: dict, field_name: str) -> dict:

        schema["properties"][field_name]["type"] = "object"
        if "oneOf" not in schema["properties"][field_name]:
            schema["properties"][field_name]["oneOf"] = schema["properties"][field_name].pop("anyOf")

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
        schema = cls.change_format_to_oneOf(schema, "credentials")
        return cls.resolve_refs(schema)
