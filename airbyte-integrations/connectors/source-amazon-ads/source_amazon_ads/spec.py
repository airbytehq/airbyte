#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List

from airbyte_cdk.models import AdvancedAuth, AuthFlowType, OAuthConfigSpecification
from airbyte_cdk.sources.utils.schema_helpers import expand_refs
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

    region: AmazonAdsRegion = Field(
        title="Region *",
        description='Region to pull data from (EU/NA/FE). See <a href=\"https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints\">docs</a> for more details.',
        default=AmazonAdsRegion.NA,
        order=0,
    )
    
    client_id: str = Field(
        title="Client ID",
        description='The client ID of your Amazon Ads developer application. See the <a href="https://advertising.amazon.com/API/docs/en-us/get-started/generate-api-tokens#retrieve-your-client-id-and-client-secret">docs</a> for more information.',
        order=1,
    )
    
    client_secret: str = Field(
        title="Client Secret",
        description='The client secret of your Amazon Ads developer application. See the <a href="https://advertising.amazon.com/API/docs/en-us/get-started/generate-api-tokens#retrieve-your-client-id-and-client-secret">docs</a> for more information.',
        airbyte_secret=True,
        order=2,
    )
    
    refresh_token: str = Field(
        title="Refresh Token",
        description='Amazon Ads refresh token. See the <a href="https://advertising.amazon.com/API/docs/en-us/get-started/generate-api-tokens">docs</a> for more information on how to obtain this token.',
        airbyte_secret=True,
        order=3,
    )

    @classmethod
    def schema(cls, **kwargs):
        schema = super().schema(**kwargs)
        expand_refs(schema)
        # Transform pydantic generated enum for region
        if schema["properties"]["region"].get("allOf"):
            schema["properties"]["region"] = {**schema["properties"]["region"]["allOf"][0], **schema["properties"]["region"]}
            schema["properties"]["region"].pop("allOf")
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
        oauth_user_input_from_connector_config_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {"region": {"type": "string", "path_in_connector_config": ["region"]}},
        },
    ),
)
