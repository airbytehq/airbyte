#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


# Basic full refresh stream
class FreshserviceStream(HttpStream, ABC):
    primary_key = "id"
    order_field = "updated_at"
    page_size = 30
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, start_date: str = None, domain_name: str = None, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self.domain_name = domain_name

    @property
    def url_base(self) -> str:
        return f"https://{self.domain_name}/api/v2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.links.get("next")
        if next_page:
            return {"page": dict(parse_qsl(urlparse(next_page.get("url")).query)).get("page")}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.page_size}

        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name


# Basic incremental stream
class IncrementalFreshserviceStream(FreshserviceStream, ABC):
    state_checkpoint_interval = 60
    cursor_field = "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["order_by"] = self.order_field
            params["order_type"] = "asc"
            if stream_state:
                params["updated_since"] = stream_state.get(self.cursor_field)
        return params


class Tickets(IncrementalFreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#view_all_ticket
    """

    object_name = "tickets"


class Problems(IncrementalFreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#problems
    """

    object_name = "problems"


class Changes(IncrementalFreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#changes
    """

    object_name = "changes"


class Releases(IncrementalFreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#releases
    """

    object_name = "releases"


class Requesters(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#requesters
    """

    object_name = "requesters"


class Agents(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#agents
    """

    object_name = "agents"


class Locations(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#locations
    """

    object_name = "locations"


class Products(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#products
    """

    object_name = "products"


class Vendors(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#vendors
    """

    object_name = "vendors"


class Assets(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#assets
    """

    object_name = "assets"


class PurchaseOrders(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#purchase-order
    """

    object_name = "purchase_orders"


class Software(FreshserviceStream):
    """
    API docs: https://api.freshservice.com/v2/#software
    """

    object_name = "applications"
