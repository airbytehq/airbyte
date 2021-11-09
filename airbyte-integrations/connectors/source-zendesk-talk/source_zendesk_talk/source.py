#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Mapping, Any, Tuple, List

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import Field, BaseModel
from requests.auth import HTTPBasicAuth
from source_zendesk_talk.streams import (
    AccountOverview,
    Addresses,
    AgentsActivity,
    AgentsOverview,
    Calls,
    CallLegs,
    CurrentQueueActivity,
    Greetings,
    GreetingCategories,
    IVRMenus,
    IVRRoutes,
    IVRs,
    PhoneNumbers,
)


class ConnectorConfig(BaseModel):
    class Config:
        title = "Zendesk Talk Spec"

    subdomain: str = Field(
        description='The subdomain for your Zendesk Talk.',
    )
    access_token: str = Field(
        description='The value of the API token generated. See the <a href=\"https://docs.airbyte.io/integrations/sources/zendesk-talk\">docs</a> for more information.',
        airbyte_secret=True,
    )
    email: str = Field(
        description='The user email for your Zendesk account.'
    )
    start_date: str = Field(
        description="The date from which you'd like to replicate data for Zendesk Talk API, in the format YYYY-MM-DDT00:00:00Z.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )


class SourceZendeskTalk(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        authenticator = HTTPBasicAuth(username=f'{config["email"]}/token', password=config["api_token"])
        stream = AccountOverview(authenticator=authenticator)

        account_info = next(stream.read_records(), default=None)
        if not account_info:
            raise RuntimeError("Unable to read account information, please check the permissions of your token")

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = ConnectorConfig.parse_obj(config)
        authenticator = HTTPBasicAuth(username=f'{config.email}/token', password=config.access_token)
        common_kwargs = dict(authenticator=authenticator, subdomain=config.subdomain)
        incremental_kwargs = dict(**common_kwargs, start_date=config.start_date)

        return [
            AccountOverview(**common_kwargs),
            Addresses(**common_kwargs),
            AgentsActivity(**common_kwargs),
            AgentsOverview(**common_kwargs),
            Calls(**incremental_kwargs),
            CallLegs(**incremental_kwargs),
            CurrentQueueActivity(**common_kwargs),
            Greetings(**common_kwargs),
            GreetingCategories(**common_kwargs),
            IVRMenus(**common_kwargs),
            IVRRoutes(**common_kwargs),
            IVRs(**common_kwargs),
            PhoneNumbers(**common_kwargs),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/zendesk-talk",
            changelogUrl="https://docs.airbyte.io/integrations/sources/zendesk-talk",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
        )
