"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys
import time

import backoff
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from enum import IntEnum
from functools import partial
from typing import Any, Callable, Iterable, Iterator, List, Mapping, Optional, Union

import pendulum as pendulum
import requests
from base_python.entrypoint import logger
from source_hubspot.errors import HubspotInvalidAuth, HubspotSourceUnavailable, HubspotRateLimited


def retry_connection_handler(**kwargs):
    """Retry helper, log each attempt"""

    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def giveup_handler(exc):
        return exc.response is not None and 400 <= exc.response.status_code < 500

    return backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=giveup_handler,
        **kwargs,
    )


def retry_after_handler(**kwargs):
    """Retry helper when we hit the call limit, sleeps for specific duration"""

    def sleep_on_ratelimit(_details):
        _, exc, _ = sys.exc_info()
        if isinstance(exc, HubspotRateLimited) and exc.response.headers.get("Retry-After"):
            retry_after = int(exc.response.headers["Retry-After"])
            logger.info(f"Rate limit reached. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_giveup(_details):
        logger.error("Max retry limit reached")

    return backoff.on_exception(
        backoff.constant,
        HubspotRateLimited,
        jitter=None,
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_giveup,
        interval=0,  # skip waiting part, we will wait in on_backoff handler
        **kwargs,
    )


class API:
    """Hubspot API interface, authorize, retrieve and post, supports backoff logic"""

    BASE_URL = "https://api.hubapi.com"
    USER_AGENT = "Airbyte"

    def __init__(self, credentials: Mapping[str, Any]):
        self._credentials = {**credentials}
        self._session = requests.Session()
        self._session.headers = {
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }

    def _acquire_access_token_from_refresh_token(self):
        payload = {
            "grant_type": "refresh_token",
            "redirect_uri": self._credentials["redirect_uri"],
            "refresh_token": self._credentials["refresh_token"],
            "client_id": self._credentials["client_id"],
            "client_secret": self._credentials["client_secret"],
        }

        resp = requests.post(self.BASE_URL + "/oauth/v1/token", data=payload)
        if resp.status_code == 403:
            raise HubspotInvalidAuth(resp.content, response=resp)

        resp.raise_for_status()
        auth = resp.json()
        self._credentials["access_token"] = auth["access_token"]
        self._credentials["refresh_token"] = auth["refresh_token"]
        self._credentials["token_expires"] = datetime.utcnow() + timedelta(seconds=auth["expires_in"] - 600)
        logger.info("Token refreshed. Expires at %s", self._credentials["token_expires"])

    @property
    def api_key(self) -> Optional[str]:
        """Get API Key if set"""
        return self._credentials.get("api_key")

    @property
    def access_token(self) -> Optional[str]:
        """Get Access Token if set, refreshes token if needed"""
        if not self._credentials.get("access_token"):
            return None

        if self._credentials["token_expires"] is None or self._credentials["token_expires"] < datetime.utcnow():
            self._acquire_access_token_from_refresh_token()
        return self._credentials.get("access_token")

    def _add_auth(self, params: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """Add auth info to request params/header"""
        params = params or {}

        if self.access_token:
            self._session.headers["Authorization"] = f"Bearer {self.access_token}"
        else:
            params["hapikey"] = self.api_key

        return params

    @staticmethod
    def _parse_and_handle_errors(response) -> Mapping[str, Any]:
        """Handle response"""
        if response.status_code == 403:
            raise HubspotSourceUnavailable(response.content)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            print(response.headers)
            print(response.json())
            raise HubspotRateLimited(
                f"429 Rate Limit Exceeded: API rate-limit has been reached until {retry_after} seconds."
                " See https://developers.hubspot.com/docs/api/usage-details",
                response=response,
            )
        else:
            response.raise_for_status()

        return response.json()

    @retry_connection_handler(max_tries=5, factor=5)
    @retry_after_handler(max_tries=3)
    def get(self, url: str, params=None) -> Union[Mapping[str, Any], List[Mapping[str, Any]]]:
        response = self._session.get(self.BASE_URL + url, params=self._add_auth(params))
        return self._parse_and_handle_errors(response)

    def post(self, url: str, data: Mapping[str, Any], params=None) -> Union[Mapping[str, Any], List[Mapping[str, Any]]]:
        response = self._session.post(self.BASE_URL + url, params=self._add_auth(params), json=data)
        return self._parse_and_handle_errors(response)


class Stream(ABC):
    """Base class for all streams. Responsible for data fetching and pagination"""

    entity = None

    more_key = None
    data_field = "results"

    page_filter = "offset"
    page_field = "offset"

    chunk_size = pendulum.interval(days=1)
    limit = 100

    def __init__(self, api: API, start_date: str = None, **kwargs):
        self._api: API = api
        self._start_date = pendulum.parse(start_date)

    @abstractmethod
    def list(self, fields) -> Iterable:
        pass

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        default_params = {"limit": self.limit, "properties": ",".join(self.properties.keys())}

        params = {**default_params, **params} if params else {**default_params}

        while True:
            response = getter(params=params)
            if response.get(self.data_field) is None:
                raise RuntimeError("Unexpected API response: {} not in {}".format(self.data_field, response.keys()))

            yield from response[self.data_field]

            # pagination
            if "paging" in response:  # APIv3 pagination
                if "next" in response["paging"]:
                    params["after"] = response["paging"]["next"]["after"]
                else:
                    break
            else:
                if not response.get(self.more_key, False):
                    break
                if self.page_field in response:
                    params[self.page_filter] = response[self.page_field]

    def read_chunked(self, getter: Callable, params: Mapping[str, Any] = None):
        params = {**params} if params else {}
        now_ts = int(pendulum.now().timestamp() * 1000)
        start_ts = int(self._start_date.timestamp() * 1000)
        chunk_size = int(self.chunk_size.total_seconds() * 1000)

        for ts in range(start_ts, now_ts, chunk_size):
            end_ts = ts + chunk_size
            params["startTimestamp"] = ts
            params["endTimestamp"] = end_ts
            logger.info(f"Reading chunk from {ts} to {end_ts}")
            yield from self.read(getter, params)

    @property
    def properties(self) -> Mapping[str, Any]:
        """Some entities has dynamic set of properties, so we trying to resolve those at runtime"""
        if not self.entity:
            return {}

        props = {}
        data = self._api.get(f"/properties/v2/{self.entity}/properties")
        for row in data:
            props[row["name"]] = {"type": row["type"]}

        return props


class CRMObjectStream(Stream):
    """ Unified stream interface for CRM objects.
        You need to provide `entity` parameter to read concrete stream, possible values are:
            campaign, company, contact, deal, line_item, owner, product, ticket, quote
        see https://developers.hubspot.com/docs/api/crm/understanding-the-crm for more details
    """

    @property
    def url(self):
        """Entity URL"""
        return f"/crm/v3/objects/{self.entity}"

    def __init__(self, entity: str, include_archived_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self._include_archived_only = include_archived_only

    def list(self, fields) -> Iterable:
        params = {
            "archived": str(self._include_archived_only).lower(),
        }
        yield from self.read(partial(self._api.get, url=self.url), params)


class CompanyStream(CRMObjectStream):
    """ Company, API v3, see CRMObjectStream for more details
        Note: Additionally gets list of contact Ids
    """
    def __init__(self, **kwargs):
        super().__init__(entity="company", **kwargs)

    def list(self, fields) -> Iterable:
        for company in super().list(fields):
            contacts = self._get_contacts(company_id=company["id"]) if "contacts" in fields else []
            company["contacts"] = contacts
            yield company

    def _get_contacts(self, company_id) -> Iterable:
        stream = CRMAssociationStream(
            entity_id=company_id, direction=CRMAssociationStream.Direction.CompanyToContact, api=self._api, start_date=self._start_date
        )
        yield from stream.list(fields=[])


class CRMAssociationStream(Stream):
    """ CRM Associations - relationships between objects
        Docs: https://legacydocs.hubspot.com/docs/methods/crm-associations/crm-associations-overview
    """
    class Direction(IntEnum):
        ContactToCompany = 1
        CompanyToContact = 2
        DealToContact = 3
        ContactToDeal = 4
        DealToCompany = 5
        CompanyToDeal = 6
        CompanyToEngagement = 7
        EngagementToCompany = 8
        ContactToEngagement = 9
        EngagementToContact = 10
        DealToEngagement = 11
        EngagementToDeal = 12
        ParentCompanyToChildCompany = 13
        ChildCompanyToParentCompany = 14
        ContactToTicket = 15
        TicketToContact = 16
        TicketToEngagement = 17
        EngagementToTicket = 18
        DealToLineItem = 19
        LineItemToDeal = 20
        CompanyToTicket = 25
        TicketToCompany = 26
        DealToTicket = 27
        TicketToDeal = 28

    more_key = "hasMore"

    def __init__(self, entity_id: int, direction: Direction, **kwargs):
        super().__init__(**kwargs)
        self.entity_id = entity_id
        self.direction = direction

    @property
    def url(self):
        return f"/crm-associations/v1/associations/{self.entity_id}/HUBSPOT_DEFINED/{self.direction}"

    def list(self, fields) -> Iterable:
        yield from self.read(partial(self._api.get, url=self.url))


class CampaignStream(Stream):
    """ Email campaigns, API v1
        Docs: https://legacydocs.hubspot.com/docs/methods/email/get_campaign_data
    """
    entity = "campaign"
    more_key = "hasMore"
    data_field = "campaigns"
    limit = 500

    def list(self, fields) -> Iterable:
        url = "/email/public/v1/campaigns/by-id"
        for row in self.read(getter=partial(self._api.get, url=url)):
            record = self._api.get(f"/email/public/v1/campaigns/{row['id']}")
            yield record


class ContactListStream(Stream):
    """ Contact lists, API v1
        Docs: https://legacydocs.hubspot.com/docs/methods/lists/get_lists
    """
    url = "contacts/v1/lists"

    def list(self, fields) -> Iterable:
        yield from self._api.get(self.url)


class DealPipelineStream(Stream):
    """ Deal pipelines, API v1,
        This endpoint requires the contacts scope the tickets scope.
        Docs: https://legacydocs.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type
    """
    url = "/crm-pipelines/v1/pipelines/deals"

    def list(self, fields) -> Iterable:
        yield from self._api.get(url=self.url)


class TicketPipelineStream(Stream):
    """ Ticket pipelines, API v1
        This endpoint requires the tickets scope.
        Docs: https://legacydocs.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type
    """
    url = "/crm-pipelines/v1/pipelines/tickets"

    def list(self, fields) -> Iterable:
        yield from self._api.get(url=self.url)


class EmailEventStream(Stream):
    """ Email events, API v1
        Docs: https://legacydocs.hubspot.com/docs/methods/email/get_events
    """
    url = "/email/public/v1/events"
    data_field = "events"
    more_key = "hasMore"
    limit = 1000

    def list(self, fields) -> Iterable:
        yield from self.read_chunked(partial(self._api.get, url=self.url))


class EngagementStream(Stream):
    """ Engagements, API v1
        Docs: https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements
    """
    entity = "engagement"
    url = "/engagements/v1/engagements/paged"
    more_key = "hasMore"
    limit = 250

    def list(self, fields) -> Iterable:
        for record in self.read(partial(self._api.get, url=self.url)):
            record["engagement_id"] = record["engagement"]["id"]
            yield record


class FormStream(Stream):
    """ Marketing Forms, API v2
        by default non-marketing forms are filtered out of this endpoint
        Docs: https://developers.hubspot.com/docs/api/marketing/forms
    """
    entity = "form"
    url = "/forms/v2/forms"

    def list(self, fields) -> Iterable:
        yield from self._api.get(self.url)


class OwnerStream(Stream):
    """ Owners, API v3
        Docs: https://legacydocs.hubspot.com/docs/methods/owners/get_owners
    """
    url = "/crm/v3/owners"

    def list(self, fields) -> Iterable:
        yield from self.read(partial(self._api.get, url=self.url))


class SubscriptionChangeStream(Stream):
    """ Subscriptions timeline for a portal, API v1
        Docs: https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions_timeline
    """
    url = "/email/public/v1/subscriptions/timeline"
    data_field = "timeline"
    more_key = "hasMore"
    limit = 1000

    def list(self, fields) -> Iterable:
        yield from self.read_chunked(partial(self._api.get, url=self.url))


class WorkflowStream(Stream):
    """ Workflows, API v3
        Docs: https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows
    """
    url = "/automation/v3/workflows"
    data_field = "workflows"

    def list(self, fields) -> Iterable:
        yield from self.read(partial(self._api.get, url=self.url))
