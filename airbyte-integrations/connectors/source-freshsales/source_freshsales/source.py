#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


# Basic full refresh stream
class FreshsalesStream(HttpStream, ABC):
    url_base = "https://{}/crm/sales/api/"
    primary_key = "id"
    order_field = "updated_at"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, domain_name: str, **kwargs):
        super().__init__(**kwargs)
        self.url_base = self.url_base.format(domain_name)
        self.domain_name = domain_name
        self.page = 1

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

    def _get_filters(self) -> List:
        """
        Some streams require a filter_id to be passed in. This function gets all available filters.
        """
        filters_url = f"https://{self.domain_name}/crm/sales/api/{self.object_name}/filters"
        auth = self.authenticator.get_auth_header()

        try:
            r = requests.get(filters_url, headers=auth)
            r.raise_for_status()
            return r.json().get("filters")
        except requests.exceptions.RequestException as e:
            raise e

    def get_view_id(self):
        """
        This function finds a relevant filter_id among all available filters by its name.
        """
        filters = self._get_filters()
        return next(_filter["id"] for _filter in filters if _filter["name"] == self.filter_name)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"


class Contacts(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#contacts
    """

    object_name = "contacts"
    filter_name = "All Contacts"


class Accounts(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#accounts
    """

    object_name = "sales_accounts"
    filter_name = "All Accounts"


class Deals(FreshsalesStream):
    object_name = "deals"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        # This is to remove data form widget development. Keeping this in failed integration tests.
        for record in records:
            record.pop("fc_widget_collaboration", None)
        yield from records


class OpenDeals(Deals):
    """
    API docs: https://developers.freshworks.com/crm/api/#deals
    """

    filter_name = "Open Deals"


class WonDeals(Deals):
    """
    API docs: https://developers.freshworks.com/crm/api/#deals
    """

    filter_name = "Won Deals"


class LostDeals(Deals):
    """
    API docs: https://developers.freshworks.com/crm/api/#deals
    """

    filter_name = "Lost Deals"


class OpenTasks(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#tasks
    """

    object_name = "tasks"
    filter_value = "open"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["filter"] = self.filter_value
        return params


class CompletedTasks(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#tasks
    """

    object_name = "tasks"
    filter_value = "completed"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["filter"] = self.filter_value
        return params


class PastAppointments(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#appointments
    """

    object_name = "appointments"
    filter_value = "past"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["filter"] = self.filter_value
        return params


class UpcomingAppointments(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#appointments
    """

    object_name = "appointments"
    filter_value = "upcoming"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["filter"] = self.filter_value
        return params


# Source
class SourceFreshsales(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = TokenAuthenticator(token=f'token={config["api_key"]}', auth_method="Token").get_auth_header()
        url = f'https://{config["domain_name"]}/crm/sales/api/contacts/filters'
        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=f'token={config["api_key"]}', auth_method="Token")
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
        ]
