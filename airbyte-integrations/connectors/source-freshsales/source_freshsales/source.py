#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class FreshsalesStream(HttpStream, ABC):
    url_base = "https://{}/crm/sales/api/"
    primary_key = "id"
    order_field = "updated_at"
    def __init__(self, domain_name: str, **kwargs):
        super().__init__(**kwargs)
        self.url_base = self.url_base.format(domain_name)
        self.domain_name = domain_name
        self.page = 1
        self.get_view_id()
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        There is no next page token in the respond so incrementing the page param until there is no new result
        """
        list_result = response.json().get(self.object_name, [])
        if list_result:
            self.page += 1
            return self.page
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"page": self.page, "sort": self.order_field, "sort_type": "asc"}  
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records
    
    def get_filters(self):
        """
        Some streams require a filter id to be passed in. This function gets the filter ids
        """
        filters_url = f"https://{self.domain_name}/crm/sales/api/{self.object_name}/filters"
        auth = self.authenticator.get_auth_header()
        try:
            r = requests.get(filters_url, headers=auth)
            r.raise_for_status()
            return r.json().get('filters')
        except requests.exceptions.RequestException as e:
            return False, e

    def get_view_id(self):
        """
        This function get the relevant filter id for the stream
        """
        if hasattr(self, "filter_name"):
            filters = self.get_filters()
            return next(filter['id'] for filter in filters if filter['name'] == self.filter_name)
        else:
            return
class Contacts(FreshsalesStream):
    object_name = "contacts"
    filter_name = "All Contacts"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"

class Accounts(FreshsalesStream):
    object_name = "sales_accounts"
    filter_name = "All Accounts"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"

class OpenDeals(FreshsalesStream):
    object_name = "deals"
    filter_name = "Open Deals"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"

class WonDeals(FreshsalesStream):
    object_name = "deals"
    filter_name = "Won Deals"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"

class LostDeals(FreshsalesStream):
    object_name = "deals"
    filter_name = "Lost Deals"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"

class OpenTasks(FreshsalesStream):
    object_name = "tasks"
    filter_value = "open"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params['filter'] = self.filter_value
        return params

class CompletedTasks(FreshsalesStream):
    object_name = "tasks"
    filter_value = "completed"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params['filter'] = self.filter_value
        return params

class PastAppointments(FreshsalesStream):
    object_name = "appointments"
    filter_value = "past"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params['filter'] = self.filter_value
        return params

class UpcomingAppointments(FreshsalesStream):
    object_name = "appointments"
    filter_value = "upcoming"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params['filter'] = self.filter_value
        return params
class SalesActivities(FreshsalesStream):
    object_name = "sales_activities"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

# Source
class FreshsalesAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"Token token={self._token}"}
class SourceFreshsales(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = FreshsalesAuthenticator(token=config["api_key"]).get_auth_header()
        url = f'https://{config["domain_name"]}/crm/sales/api/contacts/filters'
        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = FreshsalesAuthenticator(token=config["api_key"])
        args = {"authenticator": auth, "domain_name": config["domain_name"]}
        return [
            Contacts(**args),
            Accounts(**args),
            OpenDeals(**args),
            WonDeals(**args),
            LostDeals(**args),
            OpenTasks(**args),
            CompletedTasks(**args),
            PastAppointments(**args),
            UpcomingAppointments(**args),
            SalesActivities(**args)
        ]
