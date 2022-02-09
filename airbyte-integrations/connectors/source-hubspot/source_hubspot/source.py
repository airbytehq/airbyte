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
        streams = {
            "campaigns": Campaigns(**common_params),
            "companies": CRMSearchStream(
                entity="company", last_modified_field="hs_lastmodifieddate", associations=["contacts"],
                name="companies", **common_params
            ),
            "contact_lists": ContactLists(**common_params),
            "contacts": CRMSearchStream(
                entity="contact", last_modified_field="lastmodifieddate", associations=["contacts"],
                name="contacts", **common_params
            ),
            "contacts_list_memberships": ContactsListMemberships(**common_params),
            "deal_pipelines": DealPipelines(**common_params),
            "deals": Deals(associations=["contacts"], **common_params),
            "email_events": EmailEvents(**common_params),
            "engagements": Engagements(**common_params),
            "engagements_calls": CRMSearchStream(
                entity="calls", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_calls", **common_params
            ),
            "engagements_emails": CRMSearchStream(
                entity="emails", last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_emails", **common_params
            ),
            "engagements_meetings": CRMSearchStream(
                entity="meetings", last_modified_field="hs_lastmodifieddate",
                associations=["contacts", "deal", "company"],
                name="engagements_meetings", **common_params
            ),
            "engagements_notes": CRMSearchStream(
                entity="notes", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_notes", **common_params
            ),
            "engagements_tasks": CRMSearchStream(
                entity="tasks", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_tasks", **common_params
            ),
            "feedback_submissions": CRMObjectIncrementalStream(
                entity="feedback_submissions", associations=["contacts"],
                name="feedback_submissions", **common_params
            ),
            "forms": Forms(**common_params),
            "form_submissions": FormSubmissions(**common_params),
            "line_items": CRMObjectIncrementalStream(entity="line_item", name="line_items", **common_params),
            "marketing_emails": MarketingEmails(**common_params),
            "owners": Owners(**common_params),
            "products": CRMObjectIncrementalStream(entity="product", name="products", **common_params),
            "property_history": PropertyHistory(**common_params),
            "subscription_changes": SubscriptionChanges(**common_params),
            "tickets": CRMObjectIncrementalStream(entity="ticket", name="tickets", **common_params),
            "ticket_pipelines": TicketPipelines(**common_params),
            "workflows": Workflows(**common_params),
        }

        credentials_title = credentials.get("credentials_title")
        if credentials_title == "API Key Credentials":
            streams["quotes"] = CRMObjectIncrementalStream(entity="quote", name="quotes", **common_params)

        return list(streams.values())

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:  # TODO refactor use
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
