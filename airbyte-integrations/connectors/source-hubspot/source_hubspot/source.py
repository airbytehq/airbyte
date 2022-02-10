#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Mapping, Tuple, Optional, List, Iterator
from requests import HTTPError

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import AirbyteCatalog, SyncMode, AirbyteMessage
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources import AbstractSource
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
from typing import Any, MutableMapping

from airbyte_cdk.sources.deprecated.base_source import ConfiguredAirbyteStream


class SourceHubspot(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Check connection"""
        alive = True
        error_msg = None
        common_params = self.get_common_params(config=config)
        try:
            contacts = CRMSearchStream(
                entity="contact", last_modified_field="lastmodifieddate", associations=["contacts"],
                name="contacts", **common_params
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
                entity="company", last_modified_field="hs_lastmodifieddate", associations=["contacts"],
                name="companies", **common_params
            ),
            ContactLists(**common_params),
            CRMSearchStream(
                entity="contact", last_modified_field="lastmodifieddate", associations=["contacts"],
                name="contacts", **common_params
            ),
            ContactsListMemberships(**common_params),
            DealPipelines(**common_params),
            Deals(associations=["contacts"], **common_params),
            EmailEvents(**common_params),
            Engagements(**common_params),
            CRMSearchStream(
                entity="calls", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_calls", **common_params
            ),
            CRMSearchStream(
                entity="emails", last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_emails", **common_params
            ),
            CRMSearchStream(
                entity="meetings", last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_meetings", **common_params
            ),
            CRMSearchStream(
                entity="notes", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_notes", **common_params
            ),
            CRMSearchStream(
                entity="tasks", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_tasks", **common_params
            ),
            CRMObjectIncrementalStream(
                entity="feedback_submissions", associations=["contacts"],
                name="feedback_submissions", **common_params
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

    def _read_incremental(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        stream_name = configured_stream.stream.name
        stream_state = connector_state.get(stream_name, {})
        if stream_state:
            logger.info(f"Setting state of {stream_name} stream to {stream_state}")

        slices = stream_instance.stream_slices(
            cursor_field=configured_stream.cursor_field, sync_mode=SyncMode.incremental, stream_state=stream_state
        )
        total_records_counter = 0
        for slice in slices:
            records = stream_instance.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=slice,
                stream_state=stream_state,
                cursor_field=configured_stream.cursor_field or None,
            )
            for record_counter, record_data in enumerate(records, start=1):
                yield self._as_airbyte_record(stream_name, record_data)
                stream_state = stream_instance.get_updated_state(stream_state, record_data)
                checkpoint_interval = stream_instance.state_checkpoint_interval
                if checkpoint_interval and record_counter % checkpoint_interval == 0:
                    yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)

                total_records_counter += 1
                # This functionality should ideally live outside of this method
                # but since state is managed inside this method, we keep track
                # of it here.
                if self._limit_reached(internal_config, total_records_counter):
                    # Break from slice loop to save state and exit from _read_incremental function.
                    break
            # Get the stream's updated state, because state is updated after reading each chunk (if chunk is enabled), or reading all records.
            stream_state = stream_instance.get_updated_state(stream_state, latest_record=None)
            yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)
            if self._limit_reached(internal_config, total_records_counter):
                return
