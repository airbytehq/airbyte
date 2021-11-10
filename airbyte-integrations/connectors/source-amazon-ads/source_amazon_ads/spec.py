#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

from pydantic import BaseModel, Field
from source_amazon_ads.constants import AmazonAdsRegion


class AmazonAdsConfig(BaseModel):
    class Config:
        title = "Amazon Ads Spec"

    client_id: str = Field(
        name="Client ID",
        description='Oauth client id <a href="https://advertising.amazon.com/API/docs/en-us/setting-up/step-1-create-lwa-app">How to create your Login with Amazon</a>',
    )
    client_secret: str = Field(
        name="Client secret",
        description='Oauth client secret <a href="https://advertising.amazon.com/API/docs/en-us/setting-up/step-1-create-lwa-app">How to create your Login with Amazon</a>',
        airbyte_secret=True,
    )

    # Amazon docs don't describe which of the below scopes to use under what circumstances so
    # we default to the first but allow the user to override it
    scope: str = Field(
        "advertising::campaign_management",
        name="Client scope",
        examples=[
            "cpc_advertising:campaign_management",
        ],
        description="By default its advertising::campaign_management, but customers may need to set scope to cpc_advertising:campaign_management.",
    )
    refresh_token: str = Field(
        name="Oauth refresh token",
        description='Oauth 2.0 refresh_token, <a href="https://developer.amazon.com/docs/login-with-amazon/conceptual-overview.html">read details here</a>',
        airbyte_secret=True,
    )

    start_date: str = Field(
        None,
        name="Start date",
        description="Start date for collectiong reports, should not be more than 60 days in past. In YYYY-MM-DD format",
        examples=["2022-10-10", "2022-10-22"],
    )

    region: AmazonAdsRegion = Field(name="Region", description="Region to pull data from (EU/NA/FE/SANDBOX)", default=AmazonAdsRegion.NA)

    profiles: List[int] = Field(
        None,
        name="Profile Ids",
        description="profile Ids you want to fetch data for",
    )

    @classmethod
    def schema(cls, **kvargs):
        schema = super().schema(**kvargs)
        # We are using internal _host parameter to set API host to sandbox
        # environment for SAT but dont want it to be visible for end users,
        # filter out it from the jsonschema output
        schema["properties"] = {name: desc for name, desc in schema["properties"].items() if not name.startswith("_")}
        # Transform pydantic generated enum for region
        schema["definitions"]["AmazonAdsRegion"].pop("description")
        schema["properties"]["region"].update(schema["definitions"]["AmazonAdsRegion"])
        schema["properties"]["region"].pop("allOf", None)
        schema["properties"]["region"].pop("$ref", None)
        del schema["definitions"]
        return schema
