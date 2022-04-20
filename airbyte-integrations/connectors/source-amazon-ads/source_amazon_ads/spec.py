#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import List

from airbyte_cdk.models import AdvancedAuth, AuthFlowType, OAuthConfigSpecification
from pydantic import BaseModel, Extra, Field
from source_amazon_ads.constants import AmazonAdsRegion


class AmazonAdsConfig(BaseModel):
    class Config:
        title = "Amazon Ads Spec"
        # ignore extra attributes during model initialization
        # https://pydantic-docs.helpmanual.io/usage/model_config/
        extra = Extra.ignore
        # it's default, but better to be more explicit
        schema_extra = {"additionalProperties": True}

    auth_type: str = Field(default="oauth2.0", const=True, order=0)

    client_id: str = Field(
        name="Client ID",
        description=("The Client ID of your Amazon developer application."),
    )
    client_secret: str = Field(
        name="Client secret",
        description=("The Client Secret of your Amazon developer application."),
        airbyte_secret=True,
    )

    refresh_token: str = Field(
        name="Oauth refresh token",
        description=(
            'Amazon  Ads Refresh Token. See the <a href="https://docs.airbyte.io/integrations/sources/amazon-ads">docs</a> for more information on how to obtain this token.'
        ),
        airbyte_secret=True,
    )

    start_date: str = Field(
        None,
        name="Start date",
        description="Start date for collecting reports, should not be more than 60 days in past. In YYYY-MM-DD format",
        examples=["2022-10-10", "2022-10-22"],
    )

    region: AmazonAdsRegion = Field(name="Region", description="Region to pull data from (EU/NA/FE/SANDBOX)", default=AmazonAdsRegion.NA)

    profiles: List[int] = Field(
        None,
        name="Profile Ids",
        description="Profile IDs you want to fetch data for.",
    )

    report_wait_timeout: int = Field(
        name="Report Wait Timeout",
        description="Timeout duration in minutes for Reports. Eg. 30",
        default=30,
        examples=[30, 120],
    )

    report_generation_max_retries: int = Field(
        name="Report Geration Maximum Retries",
        description="Maximum retries Airbyte will attempt for fetching Report Data. Eg. 5",
        default=5,
        examples=[5, 10, 15],
    )

    @classmethod
    def schema(cls, **kwargs):
        schema = super().schema(**kwargs)
        # Transform pydantic generated enum for region
        definitions = schema.pop("definitions", None)
        if definitions:
            schema["properties"]["region"].update(definitions["AmazonAdsRegion"])
            schema["properties"]["region"].pop("allOf", None)
        return schema


advanced_auth = AdvancedAuth(
    auth_flow_type=AuthFlowType.oauth2_0,
    predicate_key=["auth_type"],
    predicate_value="oauth2.0",
    oauth_config_specification=OAuthConfigSpecification(
        complete_oauth_output_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {"refresh_token": {"type": "string", "path_in_connector_config": ["refresh_token"]}},
        },
        complete_oauth_server_input_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
        },
        complete_oauth_server_output_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "client_id": {"type": "string", "path_in_connector_config": ["client_id"]},
                "client_secret": {"type": "string", "path_in_connector_config": ["client_secret"]},
            },
        },
    ),
)
