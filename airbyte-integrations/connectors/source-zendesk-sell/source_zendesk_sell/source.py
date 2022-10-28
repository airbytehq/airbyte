#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import re
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


# Basic full refresh stream
class ZendeskSellStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..
    """

    url_base = "https://api.getbase.com/v2/"
    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            meta_links = {}
            regex_page = r"[=?/]page[_=/-]?(\d{1,3})"
            data = response.json()
            if data:
                meta_links = data.get("meta", {}).get("links")
            if "next_page" in meta_links.keys():
                return {"page": int(re.findall(regex_page, meta_links["next_page"])[0])}
            return None
        except Exception as e:
            self.logger.error(f"{e.__class__} occurred, while trying to get next page information from the following dict {meta_links}")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return {"page": next_page_token["page"]}
        else:
            return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        items = response.json()["items"]
        yield from [item["data"] for item in items]


class Pipelines(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/pipelines/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "pipelines"


class Stages(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/stages/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "stages"


class Contacts(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/contacts/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "contacts"


class Deals(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/deals/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "deals"


class Leads(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/leads/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "leads"


class CallOutcomes(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/call-outcomes/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "call_outcomes"


class Calls(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/calls/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "calls"


class Collaborations(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/collaborations/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "collaborations"


class DealSources(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/deal-sources/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "deal_sources"


class DealUnqualifiedReasons(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/deal-unqualified-reasons/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "deal_unqualified_reasons"


class LeadConversions(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/lead-conversions/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "lead_conversions"


class LeadSources(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/lead-sources/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "lead_sources"


class LeadUnqualifiedReasons(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/lead-unqualified-reasons/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "lead_unqualified_reasons"


class LossReasons(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/loss-reasons/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "loss_reasons"


class Notes(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/notes/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "notes"


class Orders(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/orders/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "orders"


class Products(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/products/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "products"


class Tags(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/tags/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "tags"


class Tasks(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/tasks/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "tasks"


class TextMessages(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/text-messages/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "text_messages"


class Users(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/users/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"


class VisitOutcomes(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/visit-outcomes/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "visit_outcomes"


class Visits(ZendeskSellStream):
    """
    Docs: https://developer.zendesk.com/api-reference/sales-crm/resources/visits/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "visits"


# Source
class SourceZendeskSell(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(token=config["api_token"])
            stream = Contacts(authenticator=authenticator)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_token"])
        return [
            Contacts(authenticator=auth),
            Deals(authenticator=auth),
            Leads(authenticator=auth),
            Pipelines(authenticator=auth),
            Stages(authenticator=auth),
            CallOutcomes(authenticator=auth),
            Calls(authenticator=auth),
            Collaborations(authenticator=auth),
            DealSources(authenticator=auth),
            DealUnqualifiedReasons(authenticator=auth),
            LeadConversions(authenticator=auth),
            LeadSources(authenticator=auth),
            LeadUnqualifiedReasons(authenticator=auth),
            LossReasons(authenticator=auth),
            Notes(authenticator=auth),
            Orders(authenticator=auth),
            Products(authenticator=auth),
            Tags(authenticator=auth),
            Tasks(authenticator=auth),
            TextMessages(authenticator=auth),
            Users(authenticator=auth),
            VisitOutcomes(authenticator=auth),
            Visits(authenticator=auth),
        ]
