#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Mapping, Any, Tuple, Optional, List
from requests import HTTPError

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import AirbyteCatalog

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
