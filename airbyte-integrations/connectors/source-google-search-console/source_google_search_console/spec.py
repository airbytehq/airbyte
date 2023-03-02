#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date
from enum import Enum
from typing import List, Optional, Union

from airbyte_cdk.models import AdvancedAuth, AuthFlowType, OAuthConfigSpecification
from airbyte_cdk.sources.config import BaseConfig
from pydantic import BaseModel, Field
from source_google_search_console.streams import SearchAnalyticsByCustomDimensions


VALID_DIMENSIONS = Enum("ValidEnums", {k: k for k in SearchAnalyticsByCustomDimensions.dimension_to_property_schema_map})
DATE_PATTERN = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
EMPTY_PATTERN = "^$"


class CustomReportConfig(BaseModel):
    class Config:
        use_enum_values = True

    name: str = Field(
        title="Name",
        description="The name of report",
    )

    dimensions: List[VALID_DIMENSIONS] = Field(title="Dimensions", description="A list of chosen dimensions", min_items=1)


class OauthAuthentication(BaseModel):
    class Config:
        title = "OAuth"

    auth_type: str = Field("Client", const=True, order=0)

    client_id: str = Field(
        title="Client ID",
        description='The client ID of your Google Search Console developer application. Read more <a href="https://developers.google.com/webmaster-tools/v1/how-tos/authorizing">here</a>.',
        airbyte_secret=True,
    )

    client_secret: str = Field(
        title="Client Secret",
        description='The client secret of your Google Search Console developer application. Read more <a href="https://developers.google.com/webmaster-tools/v1/how-tos/authorizing">here</a>.',
        airbyte_secret=True,
    )

    access_token: Optional[str] = Field(
        title="Access Token",
        description='Access token for making authenticated requests. Read more <a href="https://developers.google.com/webmaster-tools/v1/how-tos/authorizing">here</a>.',
        airbyte_secret=True,
    )

    refresh_token: str = Field(
        title="Refresh Token",
        description='The token for obtaining a new access token. Read more <a href="https://developers.google.com/webmaster-tools/v1/how-tos/authorizing">here</a>.',
        airbyte_secret=True,
    )


class ServiceAccountKeyAuthentication(BaseModel):
    class Config:
        title = "Service Account Key Authentication"

    auth_type: str = Field("Service", const=True, order=0)

    service_account_info: str = Field(
        title="Service Account JSON Key",
        description='The JSON key of the service account to use for authorization. Read more <a href="https://cloud.google.com/iam/docs/creating-managing-service-account-keys">here</a>.',
        examples=['{ "type": "service_account", "project_id": YOUR_PROJECT_ID, "private_key_id": YOUR_PRIVATE_KEY, ... }'],
        airbyte_secret=True,
    )

    email: str = Field(
        title="Admin Email",
        description="The email of the user which has permissions to access the Google Workspace Admin APIs.",
    )


class ConnectorConfig(BaseConfig):
    """Connector config"""

    class Config:
        title = "Source Google Search Console"

    authorization: Union[OauthAuthentication, ServiceAccountKeyAuthentication] = Field(
        title="Authentication Type",
        order=0,
        type="object",
    )

    site_urls: List[str] = Field(
        title="Website URL Property",
        order=1,
        description='The URLs of the website property attached to your GSC account. Read more <a href="https://support.google.com/webmasters/answer/34592?hl=en">here</a>.',
        examples=["https://example1.com/", "https://example2.com/"],
    )

    start_date: date = Field(
        title="Start Date",
        order=2,
        description="UTC date in the format 2017-01-25. Any data before this date will not be replicated.",
        examples=["2021-01-01"],
        pattern=DATE_PATTERN,
    )

    end_date: Optional[date] = Field(
        title="End Date",
        order=3,
        description=(
            "UTC date in the format 2017-01-25. Any data after this date will not be replicated. Must be greater or equal to the start date field."
        ),
        examples=["2021-12-12"],
        pattern=EMPTY_PATTERN + "|" + DATE_PATTERN,
        default_factory=lambda: date.today(),
    )

    custom_reports: Optional[List[CustomReportConfig]] = Field(
        title="Custom Reports", order=4, description="Create Analytic report by custom dimensions"
    )


advanced_auth = AdvancedAuth(
    auth_flow_type=AuthFlowType.oauth2_0,
    predicate_key=["authorization", "auth_type"],
    predicate_value="Client",
    oauth_config_specification=OAuthConfigSpecification(
        complete_oauth_output_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "access_token": {"type": "string", "path_in_connector_config": ["authorization", "access_token"]},
                "refresh_token": {"type": "string", "path_in_connector_config": ["authorization", "refresh_token"]},
                "client_id": {"type": "string", "path_in_connector_config": ["authorization", "client_id"]},
                "client_secret": {"type": "string", "path_in_connector_config": ["authorization", "client_secret"]},
            },
        },
        complete_oauth_server_input_specification={
            "type": "object",
            "additionalProperties": False,
            "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
        },
    ),
)
