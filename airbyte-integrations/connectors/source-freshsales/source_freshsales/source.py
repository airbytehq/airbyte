#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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

    primary_key: str = "id"
    order_field: str = "updated_at"
    object_name: str = None
    require_view_id: bool = False
    filter_value: str = None

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, domain_name: str, **kwargs):
        super().__init__(**kwargs)
        self.domain_name = domain_name
        self.page = 1

    @property
    def url_base(self) -> str:
        return f"https://{self.domain_name}/crm/sales/api/"

    @property
    def auth_headers(self) -> Mapping[str, Any]:
        return self.authenticator.get_auth_header()

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

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = {"page": self.page, "sort": self.order_field, "sort_type": "asc"}
        if self.filter_value:
            params["filter"] = self.filter_value
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json() or {}
        records = json_response.get(self.object_name, []) if self.object_name else json_response
        yield from records

    def _get_filters(self) -> List:
        """
        Some streams require a filter_id to be passed in. This function gets all available filters.
        """
        url = f"{self.url_base}{self.object_name}/filters"
        try:
            response = self._session.get(url=url, headers=self.auth_headers)
            response.raise_for_status()
            return response.json().get("filters")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error occured while getting `Filters` for stream `{self.name}`, full message: {e}")
            raise

    def get_view_id(self) -> int:
        """
        This function finds a relevant filter_id among all available filters by its name.
        """
        filters = self._get_filters()
        return next(_filter["id"] for _filter in filters if _filter["name"] == self.filter_name)

    def path(self, **kwargs) -> str:
        if self.require_view_id:
            return f"{self.object_name}/view/{self.get_view_id()}"
        else:
            return self.object_name


class Contacts(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#contacts
    """

    object_name = "contacts"
    filter_name = "All Contacts"
    require_view_id = True


class Accounts(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#accounts
    """

    object_name = "sales_accounts"
    filter_name = "All Accounts"
    require_view_id = True


class Deals(FreshsalesStream):
    object_name = "deals"
    require_view_id = True

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # This is to remove data form widget development. Keeping this in failed integration tests.
        for record in super().parse_response(response):
            record.pop("fc_widget_collaboration", None)
            yield record


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


class CompletedTasks(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#tasks
    """

    object_name = "tasks"
    filter_value = "completed"


class PastAppointments(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#appointments
    """

    object_name = "appointments"
    filter_value = "past"


class UpcomingAppointments(FreshsalesStream):
    """
    API docs: https://developers.freshworks.com/crm/api/#appointments
    """

    object_name = "appointments"
    filter_value = "upcoming"


# Source
class SourceFreshsales(AbstractSource):
    @staticmethod
    def get_input_stream_args(api_key: str, domain_name: str) -> Mapping[str, Any]:
        return {
            "authenticator": TokenAuthenticator(token=api_key, auth_method="Token"),
            "domain_name": domain_name,
        }

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        stream = Contacts(**self.get_input_stream_args(config["api_key"], config["domain_name"]))
        try:
            next(stream.read_records(sync_mode=None))
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self.get_input_stream_args(config["api_key"], config["domain_name"])
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
