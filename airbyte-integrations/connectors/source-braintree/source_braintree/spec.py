#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from enum import Enum

from inflection import camelize
from pydantic import BaseModel, Field, validator


class Environment(str, Enum):
    DEV = "Development"
    SANDBOX = "Sandbox"
    QA = "Qa"
    PROD = "Production"


class BraintreeConfig(BaseModel):
    class Config:
        title = "Braintree Spec"

    merchant_id: str = Field(
        name="Merchant ID",
        title="Merchant ID",
        description='The unique identifier for your entire gateway account. See the <a href="https://docs.airbyte.com/integrations/sources/braintree">docs</a> for more information on how to obtain this ID.',
    )
    public_key: str = Field(
        name="Public Key",
        title="Public Key",
        description='Braintree Public Key. See the <a href="https://docs.airbyte.com/integrations/sources/braintree">docs</a> for more information on how to obtain this key.',
    )
    private_key: str = Field(
        name="Private Key",
        title="Private Key",
        description='Braintree Private Key. See the <a href="https://docs.airbyte.com/integrations/sources/braintree">docs</a> for more information on how to obtain this key.',
        airbyte_secret=True,
    )
    start_date: datetime = Field(
        None,
        name="Start Date",
        title="Start Date",
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
        examples=["2020", "2020-12-30", "2020-11-22 20:20:05"],
    )
    environment: Environment = Field(
        name="Environment",
        title="Environment",
        description="Environment specifies where the data will come from.",
        examples=["sandbox", "production", "qa", "development"],
    )

    @validator("environment")
    def to_lower_case(cls, v):
        return v.lower()

    @validator("environment", pre=True)
    def to_camel_case(cls, v):
        return camelize(v)

    @classmethod
    def schema(cls, **kwargs):
        schema = super().schema(**kwargs)
        if "definitions" in schema:
            schema["definitions"]["Environment"].pop("description")
            schema["properties"]["environment"].update(schema["definitions"]["Environment"])
            schema["properties"]["environment"].pop("allOf", None)
            del schema["definitions"]
        return schema
