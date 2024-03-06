#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
from airbyte_cdk.models import AdvancedAuth, ConnectorSpecification, DestinationSyncMode, OAuthConfigSpecification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel, Field
from source_instagram.api import InstagramAPI
from source_instagram.streams import Media, MediaInsights, Stories, StoryInsights, UserInsights, UserLifetimeInsights, Users


class ConnectorConfig(BaseModel):
    class Config:
        title = "Source Instagram"

    start_date: Optional[datetime] = Field(
        description="The date from which you'd like to replicate data for User Insights, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated. If left blank, the start date will be set to 2 years before the present date.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    access_token: str = Field(
        description=(
            "The value of the access token generated with "
            "<b>instagram_basic, instagram_manage_insights, pages_show_list, pages_read_engagement, Instagram Public Content Access</b> "
            "permissions. "
            'See the <a href="https://docs.airbyte.com/integrations/sources/instagram/#step-1-set-up-instagram">docs</a> for more '
            "information"
        ),
        airbyte_secret=True,
    )

    client_id: Optional[str] = Field(
        description=("The Client ID for your Oauth application"),
        airbyte_secret=True,
        airbyte_hidden=True,
    )

    client_secret: Optional[str] = Field(
        description=("The Client Secret for your Oauth application"),
        airbyte_secret=True,
        airbyte_hidden=True,
    )


class SourceInstagram(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None

        try:
            self._validate_start_date(config)

            api = InstagramAPI(access_token=config["access_token"])
            logger.info(f"Available accounts: {api.accounts}")
            ok = True
        except Exception as exc:
            error_msg = repr(exc)

        return ok, error_msg

    def _validate_start_date(self, config):
        # If start_date is not found in config, set it to 2 years ago
        if not config.get("start_date"):
            config["start_date"] = pendulum.now().subtract(years=2).in_timezone("UTC").format("YYYY-MM-DDTHH:mm:ss.SSS[Z]")
        else:
            if pendulum.parse(config["start_date"]) > pendulum.now():
                raise ValueError("Please fix the start_date parameter in config, it cannot be in the future")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        api = InstagramAPI(access_token=config["access_token"])

        self._validate_start_date(config)

        return [
            Media(api=api),
            MediaInsights(api=api),
            Stories(api=api),
            StoryInsights(api=api),
            Users(api=api),
            UserLifetimeInsights(api=api),
            UserInsights(api=api, start_date=config["start_date"]),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/instagram",
            changelogUrl="https://docs.airbyte.com/integrations/sources/instagram",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
            advanced_auth=AdvancedAuth(
                auth_flow_type="oauth2.0",
                oauth_config_specification=OAuthConfigSpecification(
                    complete_oauth_output_specification={
                        "type": "object",
                        "properties": {"access_token": {"type": "string", "path_in_connector_config": ["access_token"]}},
                    },
                    complete_oauth_server_input_specification={
                        "type": "object",
                        "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
                    },
                    complete_oauth_server_output_specification={
                        "type": "object",
                        "properties": {
                            "client_id": {"type": "string", "path_in_connector_config": ["client_id"]},
                            "client_secret": {"type": "string", "path_in_connector_config": ["client_secret"]},
                        },
                    },
                ),
            ),
        )
