#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from itertools import chain
from typing import Any, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests import HTTPError
from source_hubspot.streams import (
    API,
    Campaigns,
    Companies,
    ContactLists,
    Contacts,
    ContactsListMemberships,
    CustomObject,
    DealPipelines,
    Deals,
    DealsArchived,
    EmailEvents,
    EmailSubscriptions,
    Engagements,
    EngagementsCalls,
    EngagementsEmails,
    EngagementsMeetings,
    EngagementsNotes,
    EngagementsTasks,
    Forms,
    FormSubmissions,
    Goals,
    LineItems,
    MarketingEmails,
    Owners,
    Products,
    PropertyHistory,
    SubscriptionChanges,
    TicketPipelines,
    Tickets,
    Workflows,
)


class SourceHubspot(AbstractSource):
    logger = AirbyteLogger()

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Check connection"""
        common_params = self.get_common_params(config=config)
        alive = True
        error_msg = None
        try:
            contacts = Contacts(**common_params)
            _ = contacts.properties
        except HTTPError as error:
            alive = False
            error_msg = repr(error)
        return alive, error_msg

    def get_granted_scopes(self, authenticator):
        try:
            access_token = authenticator.get_access_token()
            url = f"https://api.hubapi.com/oauth/v1/access-tokens/{access_token}"
            response = requests.get(url=url)
            response.raise_for_status()
            response_json = response.json()
            granted_scopes = response_json["scopes"]
            return granted_scopes
        except Exception as e:
            return False, repr(e)

    @staticmethod
    def get_api(config: Mapping[str, Any]) -> API:
        credentials = config.get("credentials", {})
        return API(credentials=credentials)

    def get_common_params(self, config) -> Mapping[str, Any]:
        start_date = config["start_date"]
        credentials = config["credentials"]
        api = self.get_api(config=config)
        return dict(api=api, start_date=start_date, credentials=credentials)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = config.get("credentials", {})
        common_params = self.get_common_params(config=config)
        streams = [
            Campaigns(**common_params),
            Companies(**common_params),
            ContactLists(**common_params),
            Contacts(**common_params),
            ContactsListMemberships(**common_params),
            DealPipelines(**common_params),
            Deals(**common_params),
            DealsArchived(**common_params),
            EmailEvents(**common_params),
            EmailSubscriptions(**common_params),
            Engagements(**common_params),
            EngagementsCalls(**common_params),
            EngagementsEmails(**common_params),
            EngagementsMeetings(**common_params),
            EngagementsNotes(**common_params),
            EngagementsTasks(**common_params),
            Forms(**common_params),
            FormSubmissions(**common_params),
            Goals(**common_params),
            LineItems(**common_params),
            MarketingEmails(**common_params),
            Owners(**common_params),
            Products(**common_params),
            PropertyHistory(**common_params),
            SubscriptionChanges(**common_params),
            Tickets(**common_params),
            TicketPipelines(**common_params),
            Workflows(**common_params),
        ]

        api = API(credentials=credentials)
        if api.is_oauth2():
            authenticator = api.get_authenticator()
            granted_scopes = self.get_granted_scopes(authenticator)
            self.logger.info(f"The following scopes were granted: {granted_scopes}")

            available_streams = [stream for stream in streams if stream.scope_is_granted(granted_scopes)]
            unavailable_streams = [stream for stream in streams if not stream.scope_is_granted(granted_scopes)]
            self.logger.info(f"The following streams are unavailable: {[s.name for s in unavailable_streams]}")
            partially_available_streams = [stream for stream in streams if not stream.properties_scope_is_granted()]
            required_scoped = set(chain(*[x.properties_scopes for x in partially_available_streams]))
            self.logger.info(
                f"The following streams are partially available: {[s.name for s in partially_available_streams]}, "
                f"add the following scopes to download all available data: {required_scoped}"
            )
        else:
            self.logger.info("No scopes to grant when authenticating with API key.")
            available_streams = streams

        available_streams.extend(self.get_custom_object_streams(api=api, common_params=common_params))

        return available_streams

    def get_custom_object_streams(self, api: API, common_params: Mapping[str, Any]):
        for (entity, fully_qualified_name, schema) in api.get_custom_objects_metadata():
            yield CustomObject(entity=entity, schema=schema, fully_qualified_name=fully_qualified_name, **common_params)
