#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from http import HTTPStatus
from itertools import chain
from typing import Any, Generator, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests import HTTPError
from source_hubspot.errors import HubspotInvalidAuth
from source_hubspot.streams import (
    API,
    Campaigns,
    Companies,
    CompaniesPropertyHistory,
    CompaniesWebAnalytics,
    ContactLists,
    Contacts,
    ContactsFormSubmissions,
    ContactsListMemberships,
    ContactsMergedAudit,
    ContactsPropertyHistory,
    ContactsWebAnalytics,
    CustomObject,
    DealPipelines,
    Deals,
    DealsArchived,
    DealsPropertyHistory,
    DealsWebAnalytics,
    EmailEvents,
    EmailSubscriptions,
    Engagements,
    EngagementsCalls,
    EngagementsCallsWebAnalytics,
    EngagementsEmails,
    EngagementsEmailsWebAnalytics,
    EngagementsMeetings,
    EngagementsMeetingsWebAnalytics,
    EngagementsNotes,
    EngagementsNotesWebAnalytics,
    EngagementsTasks,
    EngagementsTasksWebAnalytics,
    Forms,
    FormSubmissions,
    Goals,
    GoalsWebAnalytics,
    LineItems,
    LineItemsWebAnalytics,
    MarketingEmails,
    Owners,
    OwnersArchived,
    Products,
    ProductsWebAnalytics,
    SubscriptionChanges,
    TicketPipelines,
    Tickets,
    TicketsWebAnalytics,
    WebAnalyticsStream,
    Workflows,
)

"""
https://github.com/airbytehq/oncall/issues/3800
we use start date 2006-01-01  as date of creation of Hubspot to retrieve all data if start date was not provided

"""
DEFAULT_START_DATE = "2006-06-01T00:00:00Z"


class SourceHubspot(AbstractSource):
    logger = logging.getLogger("airbyte")

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
            if error.response.status_code == HTTPStatus.BAD_REQUEST:
                response_json = error.response.json()
                error_msg = f"400 Bad Request: {response_json['message']}, please check if provided credentials are valid."
        except HubspotInvalidAuth as e:
            alive = False
            error_msg = repr(e)
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
        start_date = config.get("start_date", DEFAULT_START_DATE)
        credentials = config["credentials"]
        api = self.get_api(config=config)
        # Additional configuration is necessary for testing certain streams due to their specific restrictions.
        acceptance_test_config = config.get("acceptance_test_config", {})
        return dict(api=api, start_date=start_date, credentials=credentials, acceptance_test_config=acceptance_test_config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = config.get("credentials", {})
        common_params = self.get_common_params(config=config)
        streams = [
            Campaigns(**common_params),
            Companies(**common_params),
            ContactLists(**common_params),
            Contacts(**common_params),
            ContactsFormSubmissions(**common_params),
            ContactsListMemberships(**common_params),
            ContactsMergedAudit(**common_params),
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
            OwnersArchived(**common_params),
            Products(**common_params),
            ContactsPropertyHistory(**common_params),
            CompaniesPropertyHistory(**common_params),
            DealsPropertyHistory(**common_params),
            SubscriptionChanges(**common_params),
            Tickets(**common_params),
            TicketPipelines(**common_params),
            Workflows(**common_params),
        ]

        enable_experimental_streams = "enable_experimental_streams" in config and config["enable_experimental_streams"]

        if enable_experimental_streams:
            streams.extend(
                [
                    ContactsWebAnalytics(**common_params),
                    CompaniesWebAnalytics(**common_params),
                    DealsWebAnalytics(**common_params),
                    TicketsWebAnalytics(**common_params),
                    EngagementsCallsWebAnalytics(**common_params),
                    EngagementsEmailsWebAnalytics(**common_params),
                    EngagementsMeetingsWebAnalytics(**common_params),
                    EngagementsNotesWebAnalytics(**common_params),
                    EngagementsTasksWebAnalytics(**common_params),
                    GoalsWebAnalytics(**common_params),
                    LineItemsWebAnalytics(**common_params),
                    ProductsWebAnalytics(**common_params),
                ]
            )

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

        custom_object_streams = list(self.get_custom_object_streams(api=api, common_params=common_params))
        available_streams.extend(custom_object_streams)

        if enable_experimental_streams:
            custom_objects_web_analytics_streams = self.get_web_analytics_custom_objects_stream(
                custom_object_stream_instances=custom_object_streams,
                common_params=common_params,
            )
            available_streams.extend(custom_objects_web_analytics_streams)

        return available_streams

    def get_custom_object_streams(self, api: API, common_params: Mapping[str, Any]):
        for entity, fully_qualified_name, schema, custom_properties in api.get_custom_objects_metadata():
            yield CustomObject(
                entity=entity,
                schema=schema,
                fully_qualified_name=fully_qualified_name,
                custom_properties=custom_properties,
                **common_params,
            )

    def get_web_analytics_custom_objects_stream(
        self, custom_object_stream_instances: List[CustomObject], common_params: Any
    ) -> Generator[WebAnalyticsStream, None, None]:
        for custom_object_stream_instance in custom_object_stream_instances:

            def __init__(self, **kwargs: Any):
                parent = custom_object_stream_instance.__class__(
                    entity=custom_object_stream_instance.entity,
                    schema=custom_object_stream_instance.schema,
                    fully_qualified_name=custom_object_stream_instance.fully_qualified_name,
                    custom_properties=custom_object_stream_instance.custom_properties,
                    **common_params,
                )
                super(self.__class__, self).__init__(parent=parent, **kwargs)

            custom_web_analytics_stream_class = type(
                f"{custom_object_stream_instance.name.capitalize()}WebAnalytics", (WebAnalyticsStream,), {"__init__": __init__}
            )

            yield custom_web_analytics_stream_class(**common_params)
