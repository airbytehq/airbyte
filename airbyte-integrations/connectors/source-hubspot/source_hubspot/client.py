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
from abc import abstractmethod, ABC
from datetime import datetime, timedelta

import pendulum as pendulum
from base_python.entrypoint import logger
from functools import partial
from typing import Mapping, Tuple, Iterable, Any, Optional, Iterator, Callable

from base_python import BaseClient
from hubspot import HubSpot
import requests


class InvalidAuthException(Exception):
    pass


class SourceUnavailableException(Exception):
    pass


class DependencyException(Exception):
    pass


class API:
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
            raise InvalidAuthException(resp.content)

        resp.raise_for_status()
        auth = resp.json()
        self._credentials["access_token"] = auth["access_token"]
        self._credentials["refresh_token"] = auth["refresh_token"]
        self._credentials["token_expires"] = datetime.utcnow() + timedelta(
            seconds=auth["expires_in"] - 600)
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

        if self._credentials["token_expires"] is None or self._credentials[
            "token_expires"] < datetime.utcnow():
            self._acquire_access_token_from_refresh_token()
        return self._credentials.get("access_token")

    def _add_auth(self, params: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """ Add auth info to request params/header
        """
        params = params or {}

        if self.api_key:
            params["hapikey"] = self.api_key
        else:
            self._session.headers["Authorization"] = f"Bearer {self.access_token}"

        return params

    @staticmethod
    def _parse_and_handle_errors(response) -> Mapping[str, Any]:
        """Handle response"""
        if response.status_code == 403:
            raise SourceUnavailableException(response.content)
        else:
            response.raise_for_status()

        return response.json()

    def get(self, url: str, params=None) -> Mapping[str, Any]:
        response = self._session.get(self.BASE_URL + url, params=self._add_auth(params))
        return self._parse_and_handle_errors(response)

    def post(self, url: str, data: Mapping[str, Any], params=None) -> Mapping[str, Any]:
        response = self._session.post(self.BASE_URL + url, params=self._add_auth(params), json=data)
        return self._parse_and_handle_errors(response)


class StreamAPI:
    more_key = ""
    data_path = ""

    page_filter = "offset"
    page_field = "offset"

    chunk_size = 1000 * 60 * 60 * 24  # TODO: use interval

    def __init__(self, api: API, start_date: str = None, **kwargs):
        self._api: API = api
        self._start_date = pendulum.parse(start_date)

    def list(self, fields) -> Iterable:
        pass

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        params = {**params} if params else {}
        while True:
            response = getter(params)
            if response.get(self.data_path) is None:
                raise RuntimeError(
                    "Unexpected API response: {} not in {}".format(self.data_path, response.keys())
                )

            for row in response[self.data_path]:
                yield row

            # pagination
            if "paging" in response:    # APIv3 pagination
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

        for ts in range(start_ts, now_ts, self.chunk_size):
            end_ts = ts + self.chunk_size
            params["startTimestamp"] = ts
            params["endTimestamp"] = end_ts
            yield from self.read(getter, params)


def lift_properties_and_versions(record):
    for key, value in record.get("properties", {}).items():
        computed_key = "property_{}".format(key)
        versions = value.get("versions")
        record[computed_key] = value

        if versions:
            if not record.get("properties_versions"):
                record["properties_versions"] = []
            record["properties_versions"] += versions
    return record


def process_v3_deals_records(v3_data):
    """
    This function:
    1. filters out fields that don"t contain "hs_date_entered_*" and
       "hs_date_exited_*"
    2. changes a key value pair in `properties` to a key paired to an
       object with a key "value" and the original value
    """
    V3_PREFIXES = {"hs_date_entered", "hs_date_exited", "hs_time_in"}

    transformed_v3_data = []
    for record in v3_data:
        new_properties = {field_name: {"value": field_value}
                          for field_name, field_value in record["properties"].items()
                          if any(prefix in field_name for prefix in V3_PREFIXES)}
        transformed_v3_data.append({**record, "properties": new_properties})
    return transformed_v3_data


class CampaignsAPI(StreamAPI):
    more_key = "hasMore"
    data_path = "campaigns"

    def list(self, fields) -> Iterable:
        url = "/email/public/v1/campaigns/by-id"
        params = {"limit": 500}
        # gen_request(STATE, url, params, "campaigns", "hasMore", ["offset"], ["offset"]):
        for row in self.read(getter=partial(self._api.get, url=url), params=params):
            record = self._api.get(f"/email/public/v1/campaigns/{row['id']}")
            yield record


class CompaniesAPI(StreamAPI):
    data_path = "companies"
    more_key = "has-more"

    def list(self, fields) -> Iterable:
        params = {
            "limit": 250, "properties": ["createdate", "hs_lastmodifieddate"]
        }

        list_url = "/companies/v2/companies/paged"
        detail_url = "/companies/v2/companies/{pk}"
        for row in self.read(partial(self._api.get, url=list_url), params):
            if fields:
                yield self._api.get(detail_url.format(pk=row["companyId"]))
            else:
                yield row


class ContactListsAPI(StreamAPI):
    data_path = "lists",
    more_key = "has-more"

    def list(self, fields) -> Iterable:
        url = "/contacts/v1/lists"
        params = {"count": 250}
        for record in self.read(partial(self._api.get, url=url), params):
            yield record


class ContactsAPI(StreamAPI):
    data_path = "contacts"
    more_key = "has-more"
    page_filter = "vid-offset"
    page_field = "vidOffset"

    def list(self, fields) -> Iterable:
        params = {
            "showListMemberships": True,
            "includeVersion": True,
            "count": 100,
        }

        url = "/contacts/v1/lists/all/contacts/all"

        vids = []
        for row in self.read(partial(self._api.get, url=url), params):
            vids.append(row["vid"])

            if len(vids) == 100:
                yield from self._sync_contact_vids(vids)
                vids = []

        if vids:
            yield from self._sync_contact_vids(vids)

    def _sync_contact_vids(self, vids):
        if len(vids) == 0:
            return

        url = "/contacts/v1/contact/vids/batch/"
        params = {
            "vid": vids,
            "showListMemberships": True,
            "formSubmissionMode": "all",
        }

        data = self._api.get(url, params=params)
        yield from data.values()


class ContactsByCompanyAPI(StreamAPI):
    def list(self, fields) -> Iterable:
        companies_api = CompaniesAPI(api=self._api)
        for company in companies_api.list(fields={}):
            yield from self._contacts_by_company(company["companyId"])

    def _contacts_by_company(self, company_id):
        url = "/companies/v2/companies/{pk}/vids".format(pk=company_id)
        # FIXME: check if pagination is possible
        params = {"count": 100}
        path = "vids"
        data = self._api.get(url, params)

        if data.get(path) is None:
            raise RuntimeError(
                "Unexpected API response: {} not in {}".format(path, data.keys())
            )

        for row in data[path]:
            yield {
                "company-id": company_id,
                "contact-id": row,
            }


class DealPipelinesAPI(StreamAPI):
    def list(self, fields) -> Iterable:
        yield from self._api.get("/deals/v1/pipelines")


def merge_responses(v1_data, v3_data):
    for v1_record in v1_data:
        v1_id = v1_record.get("dealId")
        for v3_record in v3_data:
            v3_id = v3_record.get("id")
            if str(v1_id) == v3_id:
                v1_record["properties"] = {**v1_record["properties"],
                                           **v3_record["properties"]}


class DealsAPI(StreamAPI):
    data_path = "deals"
    more_key = "hasMore"

    def list(self, fields) -> Iterable:
        params = {
            "limit": 100,
            "includeAssociations": True,
            "properties": [],
            "includeAllProperties": True,
            "allPropertiesFetchMode": "latest_version",
        }

        # Grab selected `hs_date_entered/exited` fields to call the v3 endpoint with
        v3_fields = [
            breadcrumb[1].replace("property_", "")
            for breadcrumb, mdata_map in mdata.items()
            if breadcrumb
               and (mdata_map.get("selected") or has_selected_properties)
               and any(prefix in breadcrumb[1] for prefix in V3_PREFIXES)
        ]

        url = "/deals/v1/deal/paged"
        for record in self.read(partial(self._api.get, url=url), params):
            v3_data = self._get_v3_deals(v3_fields, record)

            # The shape of v3_data is different than the V1 response,
            # so we transform v3 to look like v1
            transformed_v3_data = process_v3_deals_records(v3_data)
            merge_responses(record, transformed_v3_data)

            yield record

    def _get_v3_deals(self, v3_fields, v1_data):
        v1_ids = [{"id": str(record["dealId"])} for record in v1_data]
        v3_body = {
            "inputs": v1_ids,
            "properties": list(v3_fields[0]),
        }
        v3_url = "/crm/v3/objects/deals/batch/read"
        v3_resp = self._api.post(v3_url, data=v3_body)
        return v3_resp["results"]


ENDPOINTS = {
    "contacts_properties": "/properties/v1/contacts/properties",
    "contacts_all": "/contacts/v1/lists/all/contacts/all",
    "contacts_recent": "/contacts/v1/lists/recently_updated/contacts/recent",
    "contacts_detail": "/contacts/v1/contact/vids/batch/",

    "companies_properties": "/companies/v2/properties",
    "companies_all": "/companies/v2/companies/paged",
    "companies_recent": "/companies/v2/companies/recent/modified",
    "companies_detail": "/companies/v2/companies/{company_id}",
    "contacts_by_company": "/companies/v2/companies/{company_id}/vids",

    "deals_properties": "/properties/v1/deals/properties",
    "deals_all": "/deals/v1/deal/paged",
    "deals_recent": "/deals/v1/deal/recent/modified",
    "deals_detail": "/deals/v1/deal/{deal_id}",

    "deals_v3_batch_read": "/crm/v3/objects/deals/batch/read",
    "deals_v3_properties": "/crm/v3/properties/deals",

    "deal_pipelines": "/deals/v1/pipelines",

    "campaigns_all": "/email/public/v1/campaigns/by-id",
    "campaigns_detail": "/email/public/v1/campaigns/{campaign_id}",

    "engagements_all": "",

    "subscription_changes": "/email/public/v1/subscriptions/timeline",
    "email_events": "/email/public/v1/events",
    "contact_lists": "/contacts/v1/lists",
    "forms": "/forms/v2/forms",
    "workflows": "/automation/v3/workflows",
    "owners": "/owners/v2/owners",
}


class EmailEventsAPI(StreamAPI):
    data_path = "events"
    more_key = "hasMore"

    def list(self, field) -> Iterable:
        params = {"limit": 1000, }
        url = "/email/public/v1/subscriptions/timeline"

        yield from self.read_chunked(partial(self._api.get, url=url), params=params)


class EngagementsAPI(StreamAPI):
    data_path = "results"
    more_key = "hasMore"

    def list(self, fields) -> Iterable:
        url = "/engagements/v1/engagements/paged"
        params = {"limit": 250}
        for record in self.read(partial(self._api.get, url=url), params):
            record["engagement_id"] = record["engagement"]["id"]
            yield record


class FormsAPI(StreamAPI):
    def list(self, fields) -> Iterable:
        for row in self._api.get("/forms/v2/forms"):
            yield row


class CRMObjectsAPI(StreamAPI, ABC):
    @property
    @abstractmethod
    def url(self):
        """Endpoint URL"""

    limit = 100
    data_path = "results"

    def __init__(self, include_archived_only=False, **kwargs):
        super().__init__(**kwargs)
        self._include_archived_only = include_archived_only

    def list(self, field) -> Iterable:
        params = {
            "limit": self.limit,
            "archived": self._include_archived_only
        }
        for record in self.read(partial(self._api.get, url=self.url), params):
            yield record


class LineItemsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/line_items"


class ProductsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/products"


class QuotesAPI(CRMObjectsAPI):
    url = "crm/v3/objects/quotes"


class TicketsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/tickets"


class OwnersAPI(StreamAPI):
    def __init__(self, include_inactive=False, **kwargs):
        super().__init__(**kwargs)
        self._include_inactive = include_inactive

    def list(self, fields) -> Iterable:
        params = {}
        if self._include_inactive:
            params["includeInactives"] = "true"

        for record in self._api.get("/owners/v2/owners", params):
            yield record


class SubscriptionChangesAPI(StreamAPI):
    data_path = "timeline"
    more_key = "hasMore"

    def list(self, field) -> Iterable:
        params = {"limit": 1000, }
        url = "/email/public/v1/subscriptions/timeline"

        yield from self.read_chunked(partial(self._api.get, url=url), params=params)


class WorkflowsAPI(StreamAPI):
    def list(self, field) -> Iterable:
        data = self._api.get("/automation/v3/workflows")
        for record in data["workflows"]:
            yield record


class Client(BaseClient):
    def __init__(self, start_date, credentials, **kwargs):
        self._start_date = start_date
        self._client = HubSpot(api_key=credentials["api_key"])
        self._api = API(credentials=credentials)

        self._apis = {
            "campaigns": CampaignsAPI(api=self._api),
            "companies": CompaniesAPI(api=self._api),
            "contact_lists": ContactListsAPI(api=self._api),
            "contacts": ContactsAPI(api=self._api),
            "contacts_by_company": ContactsByCompanyAPI(api=self._api),
            "deal_pipelines": DealPipelinesAPI(api=self._api),
            "deals": DealsAPI(api=self._api),
            "email_events": EmailEventsAPI(api=self._api),
            "engagements": EngagementsAPI(api=self._api),
            "forms": FormsAPI(api=self._api),
            "line_items": LineItemsAPI(api=self._api),
            "owners": OwnersAPI(api=self._api),
            "products": ProductsAPI(api=self._api),
            "quotes": QuotesAPI(api=self._api),
            "subscription_changes": SubscriptionChangesAPI(api=self._api),
            "tickets": TicketsAPI(api=self._api),
            "workflows": WorkflowsAPI(api=self._api),
        }

        super().__init__(**kwargs)

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        pass
