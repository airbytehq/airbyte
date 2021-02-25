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
from typing import Mapping, Iterable, Any, Optional, Iterator, Callable

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


class StreamAPI(ABC):
    more_key = None
    data_path = "results"

    page_filter = "offset"
    page_field = "offset"

    chunk_size = 1000 * 60 * 60 * 24  # TODO: use interval
    limit = 100

    def __init__(self, api: API, start_date: str = None, **kwargs):
        self._api: API = api
        self._start_date = pendulum.parse(start_date)

    @abstractmethod
    def list(self, fields) -> Iterable:
        pass

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        default_params = {
            "limit": self.limit
        }
        params = {**default_params, **params} if params else {**default_params}

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

    def list(self, fields) -> Iterable:
        params = {
            "limit": self.limit,
            "archived": self._include_archived_only
        }
        for record in self.read(partial(self._api.get, url=self.url), params):
            yield record


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


class CompaniesAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/companies"
    limit = 250


class ContactListsAPI(CRMObjectsAPI):
    limit = 250
    url = "/crm/v3/objects/contacts"


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


class EmailEventsAPI(StreamAPI):
    data_path = "events"
    more_key = "hasMore"

    def list(self, fields) -> Iterable:
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


class ContactsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/contacts"


class DealsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/deals"


class LineItemsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/line_items"


class ProductsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/products"


class QuotesAPI(CRMObjectsAPI):
    url = "crm/v3/objects/quotes"


class TicketsAPI(CRMObjectsAPI):
    url = "/crm/v3/objects/tickets"


class OwnersAPI(StreamAPI):
    url = "/crm/v3/owners"
    data_path = "results"

    def list(self, fields) -> Iterable:
        yield from self.read(partial(self._api.get, url=self.url))


class SubscriptionChangesAPI(StreamAPI):
    url = "/email/public/v1/subscriptions/timeline"
    data_path = "timeline"
    more_key = "hasMore"
    limit = 1000

    def list(self, fields) -> Iterable:
        yield from self.read_chunked(partial(self._api.get, url=self.url))


class WorkflowsAPI(StreamAPI):
    def list(self, fields) -> Iterable:
        data = self._api.get("/automation/v3/workflows")
        for record in data["workflows"]:
            yield record
