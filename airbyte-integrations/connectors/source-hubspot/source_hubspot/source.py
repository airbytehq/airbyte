#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from http import HTTPStatus
from itertools import chain
from typing import Any, List, Mapping, Optional, Tuple

from datetime import datetime, timedelta
import requests
from airbyte_cdk.entrypoint import logger as entrypoint_logger
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, NoopCursor
from airbyte_cdk.sources.streams.concurrent.state_converter import AscendingValueConcurrentStreamStateConverter
from requests import HTTPError

from source_hubspot.errors import HubspotInvalidAuth
from source_hubspot.streams import (
    API,
    Campaigns,
    ClientSideIncrementalStream,
    Companies,
    ContactLists,
    Contacts,
    ContactsListMemberships,
    ContactsMergedAudit,
    CRMObjectIncrementalStream,
    CRMSearchStream,
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
    OwnersArchived,
    Products,
    PropertyHistory,
    SubscriptionChanges,
    TicketPipelines,
    Tickets,
    Workflows,
)


def _incremental_iso8601_datetime(formats: List[str], delta: timedelta):
    def _increment(timestamp: str):
        for format in formats:
            try:
                return (datetime.strptime(timestamp, format) + delta).strftime(format)
            except Exception:
                pass
        raise ValueError("_incremental_iso8601_datetime")
    return _increment


class SourceHubspot(AbstractSource):
    logger = AirbyteLogger()
    message_repository = InMemoryMessageRepository(entrypoint_logger.level)

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
            PropertyHistory(**common_params),
            SubscriptionChanges(**common_params),
            Tickets(**common_params),
            TicketPipelines(**common_params),
            Workflows(**common_params),
        ]
        state_manager = ConnectorStateManager(stream_instance_map={s.name: s for s in streams},
                                              state=self.read_state("sample_files/sample_state.json"))
        for stream in streams:
            if isinstance(stream, ClientSideIncrementalStream):
                stream._lowest_cursor_value = state_manager.get_stream_state(stream.name, stream.namespace).get(stream.cursor_field)

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

        concurrent_streams = []
        epoch_cursor_value_stream = {'contact_lists', 'email_events', 'workflows', 'deal_pipelines', 'subscription_changes', 'engagements', 'campaigns'}
        iso8601_cursor_value_stream = {'engagements_tasks', 'engagements_meetings', 'owners', 'products', 'contacts', 'companies', 'forms', 'goals', 'engagements_calls', 'engagements_notes', 'deals_archived', 'tickets', 'deals', 'line_items', 'engagements_emails'}
        for stream in available_streams:
            if stream.name in epoch_cursor_value_stream:
                state_converter = AscendingValueConcurrentStreamStateConverter(stream.cursor_field, 0, lambda x: x + 1)
                state = state_converter.get_concurrent_stream_state(
                    state_manager.get_stream_state(stream.name, stream.namespace)
                )
                cursor = ConcurrentCursor(
                    stream.name,
                    stream.namespace,
                    state,
                    self.message_repository,
                    state_manager,
                    state_converter,
                    CursorField(stream.cursor_field[0] if type(stream.cursor_field) == list else stream.cursor_field),
                    () if isinstance(stream, (ClientSideIncrementalStream, CRMObjectIncrementalStream, CRMSearchStream, Engagements)) else ("startTimestamp", "endTimestamp"),
                )
            elif stream.name in iso8601_cursor_value_stream:
                state_converter = AscendingValueConcurrentStreamStateConverter(stream.cursor_field, "0001-01-01T00:00:00Z", _incremental_iso8601_datetime(["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"], timedelta(seconds=1)))
                state = state_converter.get_concurrent_stream_state(
                    state_manager.get_stream_state(stream.name, stream.namespace)
                )
                cursor = ConcurrentCursor(
                    stream.name,
                    stream.namespace,
                    state,
                    self.message_repository,
                    state_manager,
                    state_converter,
                    CursorField(stream.cursor_field[0] if type(stream.cursor_field) == list else stream.cursor_field),
                    () if isinstance(stream, (ClientSideIncrementalStream, CRMObjectIncrementalStream, CRMSearchStream, Engagements)) else ("startTimestamp", "endTimestamp"),
                )
            else:
                state = {}
                cursor = NoopCursor()

            concurrent_streams.append(
                StreamFacade.create_from_stream(
                    stream,
                    self,
                    entrypoint_logger,
                    5,
                    state,
                    cursor,
                )
            )
        return concurrent_streams

    def get_custom_object_streams(self, api: API, common_params: Mapping[str, Any]):
        for entity, fully_qualified_name, schema, custom_properties in api.get_custom_objects_metadata():
            yield CustomObject(
                entity=entity,
                schema=schema,
                fully_qualified_name=fully_qualified_name,
                custom_properties=custom_properties,
                **common_params,
            )
