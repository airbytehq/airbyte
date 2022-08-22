#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel, Field
from requests.auth import HTTPBasicAuth
from source_zendesk_talk.streams import (
    AccountOverview,
    Addresses,
    AgentsActivity,
    AgentsOverview,
    CallLegs,
    Calls,
    CurrentQueueActivity,
    GreetingCategories,
    Greetings,
    IVRMenus,
    IVRRoutes,
    IVRs,
    PhoneNumbers,
)


class ConnectorConfig(BaseModel):
    class Config:
        title = "Zendesk Talk Spec"

    subdomain: str = Field(
        description="The subdomain for your Zendesk Talk.",
    )
    access_token: str = Field(
        description='The value of the API token generated. See the <a href="https://docs.airbyte.io/integrations/sources/zendesk-talk">docs</a> for more information.',
        airbyte_secret=True,
    )
    email: str = Field(description="The user email for your Zendesk account.")
    start_date: datetime = Field(
        title="Replication Start Date",
        description="The date/datetime from which you'd like to replicate data for Zendesk Talk API, in the format YYYY-MM-DDT00:00:00Z. The time part is optional.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)?$",
        examples=["2017-01-25T00:00:00Z", "2017-01-25"],
    )


class SourceZendeskTalk(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        parsed_config = ConnectorConfig.parse_obj(config)
        authenticator = HTTPBasicAuth(username=f"{parsed_config.email}/token", password=parsed_config.access_token)
        stream = AccountOverview(authenticator=authenticator, subdomain=parsed_config.subdomain)

        account_info = next(iter(stream.read_records(sync_mode=SyncMode.full_refresh)), None)
        if not account_info:
            raise RuntimeError("Unable to read account information, please check the permissions of your token")

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        parsed_config = ConnectorConfig.parse_obj(config)
        authenticator = HTTPBasicAuth(username=f"{parsed_config.email}/token", password=parsed_config.access_token)
        common_kwargs = dict(authenticator=authenticator, subdomain=parsed_config.subdomain)
        incremental_kwargs = dict(**common_kwargs, start_date=parsed_config.start_date)

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
