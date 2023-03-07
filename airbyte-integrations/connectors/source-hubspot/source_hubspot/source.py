#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from itertools import chain
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from requests import HTTPError
from source_hubspot.constants import API_KEY_CREDENTIALS
from source_hubspot.streams import (
    API,
    Campaigns,
    Companies,
    ContactLists,
    Contacts,
    ContactsListMemberships,
    DealPipelines,
    Deals,
    EmailEvents,
    Engagements,
    EngagementsCalls,
    EngagementsEmails,
    EngagementsMeetings,
    EngagementsNotes,
    EngagementsTasks,
    Forms,
    FormSubmissions,
    LineItems,
    MarketingEmails,
    Owners,
    Products,
    PropertyHistory,
    Quotes,
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
            EmailEvents(**common_params),
            Engagements(**common_params),
            EngagementsCalls(**common_params),
            EngagementsEmails(**common_params),
            EngagementsMeetings(**common_params),
            EngagementsNotes(**common_params),
            EngagementsTasks(**common_params),
            Forms(**common_params),
            FormSubmissions(**common_params),
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

        credentials_title = credentials.get("credentials_title")
        if credentials_title == API_KEY_CREDENTIALS:
            streams.append(Quotes(**common_params))

        api = API(credentials=credentials)
        if api.is_oauth2():
            authenticator = API(credentials=credentials).get_authenticator()
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

        return available_streams

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        """
        This method is overridden to check whether the stream `quotes` exists in the source, if not skip reading that stream.
        """
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state)
        self._stream_to_instance_map = stream_instances
        with create_timer(self.name) as timer:
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(configured_stream.stream.name)
                if not stream_instance and configured_stream.stream.name == "quotes":
                    logger.warning("Stream `quotes` does not exist in the source. Skip reading `quotes` stream.")
                    continue
                if not stream_instance:
                    raise KeyError(
                        f"The requested stream {configured_stream.stream.name} was not found in the source. Available streams: {stream_instances.keys()}"
                    )

                try:
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        state_manager=state_manager,
                        internal_config=internal_config,
                    )
                except Exception as e:
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    display_message = stream_instance.get_error_display_message(e)
                    if display_message:
                        raise AirbyteTracedException.from_exception(e, message=display_message) from e
                    raise e
                finally:
                    logger.info(f"Finished syncing {self.name}")
                    logger.info(timer.report())

        logger.info(f"Finished syncing {self.name}")
