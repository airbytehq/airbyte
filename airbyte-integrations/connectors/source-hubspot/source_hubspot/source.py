#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import AirbyteCatalog, AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.deprecated.base_source import ConfiguredAirbyteStream
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.utils.event_timing import create_timer
from requests import HTTPError
from source_hubspot.api import (
    API,
    Campaigns,
    ContactLists,
    ContactsListMemberships,
    CRMObjectIncrementalStream,
    CRMSearchStream,
    DealPipelines,
    Deals,
    EmailEvents,
    Engagements,
    Forms,
    FormSubmissions,
    MarketingEmails,
    Owners,
    PropertyHistory,
    SubscriptionChanges,
    TicketPipelines,
    Workflows,
)


class SourceHubspot(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Check connection"""
        alive = True
        error_msg = None
        common_params = self.get_common_params(config=config)
        try:
            contacts = CRMSearchStream(
                entity="contact", last_modified_field="lastmodifieddate", associations=["contacts"], name="contacts", **common_params
            )
            _ = contacts.properties
        except HTTPError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg

    @staticmethod
    def get_api(config: Mapping[str, Any]):
        credentials = config.get("credentials", {})
        return API(credentials=credentials)

    def get_common_params(self, config):
        start_date = config.get("start_date")
        api = self.get_api(config=config)
        common_params = dict(api=api, start_date=start_date)
        return common_params

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = config.get("credentials", {})
        common_params = self.get_common_params(config=config)
        streams = [
            Campaigns(**common_params),
            CRMSearchStream(
                entity="company", last_modified_field="hs_lastmodifieddate", associations=["contacts"], name="companies", **common_params
            ),
            ContactLists(**common_params),
            CRMSearchStream(
                entity="contact", last_modified_field="lastmodifieddate", associations=["contacts"], name="contacts", **common_params
            ),
            ContactsListMemberships(**common_params),
            DealPipelines(**common_params),
            Deals(associations=["contacts"], **common_params),
            EmailEvents(**common_params),
            Engagements(**common_params),
            CRMSearchStream(
                entity="calls",
                last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_calls",
                **common_params,
            ),
            CRMSearchStream(
                entity="emails",
                last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_emails",
                **common_params,
            ),
            CRMSearchStream(
                entity="meetings",
                last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_meetings",
                **common_params,
            ),
            CRMSearchStream(
                entity="notes",
                last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_notes",
                **common_params,
            ),
            CRMSearchStream(
                entity="tasks",
                last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_tasks",
                **common_params,
            ),
            CRMObjectIncrementalStream(
                entity="feedback_submissions", associations=["contacts"], name="feedback_submissions", **common_params
            ),
            Forms(**common_params),
            FormSubmissions(**common_params),
            CRMObjectIncrementalStream(entity="line_item", name="line_items", **common_params),
            MarketingEmails(**common_params),
            Owners(**common_params),
            CRMObjectIncrementalStream(entity="product", name="products", **common_params),
            PropertyHistory(**common_params),
            SubscriptionChanges(**common_params),
            CRMObjectIncrementalStream(entity="ticket", name="tickets", **common_params),
            TicketPipelines(**common_params),
            Workflows(**common_params),
        ]

        credentials_title = credentials.get("credentials_title")
        if credentials_title == "API Key Credentials":
            streams.append(CRMObjectIncrementalStream(entity="quote", name="quotes", **common_params))

        return streams

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """List of available streams, patch streams to append properties dynamically"""
        streams = []
        for stream_instance in self.streams(config=config):
            stream = stream_instance.as_airbyte_stream()
            properties = stream_instance.properties
            if properties:
                stream.json_schema["properties"]["properties"] = {"type": "object", "properties": properties}
                stream.default_cursor_field = [stream_instance.updated_at_field]
            streams.append(stream)

        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: logging.Logger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ) -> Iterator[AirbyteMessage]:
        """
        This method is overridden to check whether the stream `quotes` exists in the source, if not skip reading that stream.
        """
        connector_state = copy.deepcopy(state or {})
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
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
                        connector_state=connector_state,
                        internal_config=internal_config,
                    )
                except Exception as e:
                    logger.exception(f"Encountered an exception while reading stream {self.name}")
                    raise e
                finally:
                    logger.info(f"Finished syncing {self.name}")
                    logger.info(timer.report())

        logger.info(f"Finished syncing {self.name}")

    def _read_incremental(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        """
        This method is overridden to checkpoint the latest actual state,
        because stream state is refreshed after reading each batch of records (if need_chunk is True),
        or reading all records in the stream.
        """
        yield from super()._read_incremental(
            logger=logger,
            stream_instance=stream_instance,
            configured_stream=configured_stream,
            connector_state=connector_state,
            internal_config=internal_config,
        )
        stream_name = configured_stream.stream.name
        stream_state = stream_instance.get_updated_state(current_stream_state={}, latest_record={})
        yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)
