#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
        description='<a href="https://docs.airbyte.io/integrations/sources/braintree">Merchant ID</a> is the unique identifier for entire gateway account.',
    )
    public_key: str = Field(name="Public key", description="This is your user-specific public identifier for Braintree.")
    private_key: str = Field(name="Private Key", description="This is your user-specific private identifier.", airbyte_secret=True)
    start_date: datetime = Field(
        None,
        name="Start date",
        description="The date from which you'd like to replicate data for Braintree API for UTC timezone, All data generated after this date will be replicated.",
        examples=["2020", "2020-12-30", "2020-11-22 20:20:05"],
    )
    environment: Environment = Field(
        name="Environment",
        description="Environment specifies where the data will come from.",
        examples=["sandbox", "production", "qa", "development"],
    )

    @validator("environment")
    def to_lower_case(cls, v):
        return v.lower()

    @validator("environment", pre=True)
    def to_camel_case(cls, v):
        return camelize(v)
