#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import AuthSpecification, ConnectorSpecification, OAuth2Specification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from pydantic import Field
from pydantic.main import BaseModel

from .streams import Applications, Interviews, Notes, Offers, Opportunities, Referrals, Users


class ConnectorConfig(BaseModel):
    class Config:
        title = "Lever Hiring Spec"

    client_id: str = Field(
        description="The client application id as provided when registering the application with Lever.",
    )
    client_secret: str = Field(
        description="The application secret as provided when registering the application with Lever.",
        airbyte_secret=True,
    )
    refresh_token: str = Field(
        description="The refresh token your application will need to submit to get a new access token after it's expired.",
    )
    environment: str = Field(description="Sandbox or Production environment.", enum=["Sandbox", "Production"], default="Production")
    start_date: str = Field(
        description="UTC date and time in the format 2019-02-25T00:00:00Z. Any data before this date will not be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2021-04-25T00:00:00Z"],
    )


class SourceLeverHiring(AbstractSource):
    URL_MAP_ACCORDING_ENVIRONMENT = {
        "Sandbox": {"login": "https://sandbox-lever.auth0.com/", "api": "https://api.sandbox.lever.co/"},
        "Production": {"login": "https://auth.lever.co/", "api": "https://api.lever.co/"},
    }

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        authenticator = Oauth2Authenticator(
            token_refresh_endpoint=f"{self.URL_MAP_ACCORDING_ENVIRONMENT[config['environment']]['login']}oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )
        _ = authenticator.get_auth_header()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = Oauth2Authenticator(
            token_refresh_endpoint=f"{self.URL_MAP_ACCORDING_ENVIRONMENT[config['environment']]['login']}oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )
        full_refresh_params = {"authenticator": authenticator, "base_url": self.URL_MAP_ACCORDING_ENVIRONMENT[config["environment"]]["api"]}
        stream_params_with_start_date = {**full_refresh_params, "start_date": config["start_date"]}
        return [
            Applications(**stream_params_with_start_date),
            Interviews(**stream_params_with_start_date),
            Notes(**stream_params_with_start_date),
            Offers(**stream_params_with_start_date),
            Opportunities(**stream_params_with_start_date),
            Referrals(**stream_params_with_start_date),
            Users(**full_refresh_params),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/lever-hiring",
            changelogUrl="https://docs.airbyte.io/integrations/sources/lever-hiring#changelog",
            connectionSpecification=ConnectorConfig.schema(),
            authSpecification=AuthSpecification(
                auth_type="oauth2.0",
                oauth2Specification=OAuth2Specification(oauthFlowInitParameters=[["client_id"], ["client_secret"], ["refresh_token"]]),
            ),
        )
