#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AdvancedAuth, AuthFlowType, OAuthConfigSpecification
from pydantic import BaseModel, Field
from source_amazon_seller_partner.constants import AWSEnvironment, AWSRegion


class AmazonSellerPartnerConfig(BaseModel):
    class Config:
        title = "Amazon Seller Partner Spec"
        schema_extra = {"additionalProperties": True}

    app_id: str = Field(
        None,
        description="Your Amazon App ID",
        title="App Id",
        airbyte_secret=True,
        order=0,
    )

    auth_type: str = Field(
        default="oauth2.0",
        const=True,
        order=1,
    )

    lwa_app_id: str = Field(
        description="Your Login with Amazon Client ID.",
        title="LWA Client Id",
        order=2,
    )

    lwa_client_secret: str = Field(
        description="Your Login with Amazon Client Secret.",
        title="LWA Client Secret",
        airbyte_secret=True,
        order=3,
    )

    refresh_token: str = Field(
        description="The Refresh Token obtained via OAuth flow authorization.",
        title="Refresh Token",
        airbyte_secret=True,
        order=4,
    )

    aws_access_key: str = Field(
        description="Specifies the AWS access key used as part of the credentials to authenticate the user.",
        title="AWS Access Key",
        airbyte_secret=True,
        order=5,
    )

    aws_secret_key: str = Field(
        description="Specifies the AWS secret key used as part of the credentials to authenticate the user.",
        title="AWS Secret Access Key",
        airbyte_secret=True,
        order=6,
    )

    role_arn: str = Field(
        description="Specifies the Amazon Resource Name (ARN) of an IAM role that you want to use to perform operations requested using this profile. (Needs permission to 'Assume Role' STS).",
        title="Role ARN",
        airbyte_secret=True,
        order=7,
    )

    replication_start_date: str = Field(
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
        title="Start Date",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
        order=8,
    )

    replication_end_date: str = Field(
        None,
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any data after this date will not be replicated.",
        title="End Date",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$|^$",
        examples=["2017-01-25T00:00:00Z"],
        order=9,
    )

    period_in_days: int = Field(
        90,
        le=90,
        examples=["1", "10", "30", "60", "90"],
        description="Will be used for stream slicing for initial full_refresh sync when no updated state is present for reports that support sliced incremental sync.",
        order=10,
    )
    report_options: str = Field(
        None,
        description="Additional information passed to reports. This varies by report type. Must be a valid json string.",
        examples=['{"GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT": {"reportPeriod": "WEEK"}}', '{"GET_SOME_REPORT": {"custom": "true"}}'],
        order=11,
    )
    max_wait_seconds: int = Field(
        500,
        title="Max wait time for reports (in seconds)",
        description="Sometimes report can take up to 30 minutes to generate. This will set the limit for how long "
        "to wait for a successful report.",
        examples=["500", "1980"],
        order=12,
    )

    aws_environment: AWSEnvironment = Field(
        description="Select the AWS Environment.",
        title="AWS Environment",
    )

    region: AWSRegion = Field(
        description="Select the AWS Region.",
        title="AWS Region",
    )


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
            "properties": {"lwa_app_id": {"type": "string"}, "lwa_client_secret": {"type": "string"}},
        },
        complete_oauth_server_output_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "lwa_app_id": {"type": "string", "path_in_connector_config": ["lwa_app_id"]},
                "lwa_client_secret": {"type": "string", "path_in_connector_config": ["lwa_client_secret"]},
            },
        },
        oauth_user_input_from_connector_config_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {"app_id": {"type": "string", "path_in_connector_config": ["app_id"]}},
        },
    ),
)
