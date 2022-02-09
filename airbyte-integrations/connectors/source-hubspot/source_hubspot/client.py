#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Callable, Iterator, Mapping, Optional, Tuple

from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.sources.deprecated.client import BaseClient
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


class Client(BaseClient):
    """HubSpot client, provides methods to discover and read streams"""

    def __init__(self, start_date, credentials, **kwargs):
        self._start_date = start_date
        self._api = API(credentials=credentials)

        common_params = dict(api=self._api, start_date=self._start_date)
        self._apis = {
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
                entity="emails", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
                name="engagements_emails", **common_params
            ),
            "engagements_meetings": CRMSearchStream(
                entity="meetings", last_modified_field="hs_lastmodifieddate", associations=["contacts", "deal", "company"],
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
            self._apis["quotes"] = CRMObjectIncrementalStream(entity="quote", name="quotes", **common_params)

        super().__init__(**kwargs)

    def _enumerate_methods(self) -> Mapping[str, Callable]:
        return {name: api.list_records for name, api in self._apis.items()}

    # @property
    # def streams(self) -> Iterator[AirbyteStream]:
    #     """List of available streams, patch streams to append properties dynamically"""
    #     for stream in super().streams:
    #         properties = self._apis[stream.name].properties
    #         if properties:
    #             stream.json_schema["properties"]["properties"] = {"type": "object", "properties": properties}
    #             stream.default_cursor_field = [self._apis[stream.name].updated_at_field]
    #         yield stream

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], "state")

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    def health_check(self) -> Tuple[bool, Optional[str]]:
        alive = True
        error_msg = None

        try:
            _ = self._apis["contacts"].properties
        except HTTPError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg

    def get_stream_instances(self):  # refactor
        return list(self._apis.values())
