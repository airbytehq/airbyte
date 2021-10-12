from abc import ABC
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from urllib.parse import parse_qsl, urlparse

from typing import Any, Iterable, Dict, Mapping, MutableMapping, Optional


# Basic full refresh stream
class FreshserviceStream(HttpStream, ABC):
    url_base = "https://{}/api/v2/"
    primary_key = "id"
    order_field = "updated_at"
    results_per_page = 30

    def __init__(self, config: Dict):
        super().__init__(authenticator=config['authenticator'])
        self.config = config
        self.url_base = self.url_base.format(config['domain_name'])

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "per_page": self.results_per_page
        }
        if next_page_token:
            params.update(**next_page_token)
        else:
            params["order_by"] = self.order_field
            params["order_type"] = "asc"
            params["updated_since"] = self.config["start_date"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records

class FullRefrehsFreshserviceStream(FreshserviceStream, ABC):
    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.pop("updated_since")
        params.pop("order_type")
        params.pop("order_by")
        return params

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

    # Parse the stream_slice with respect to stream_state for Incremental refresh
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            for record in records_slice:
                if record.get(self.cursor_field) >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class Tickets(IncrementalFreshserviceStream):
    object_name = 'tickets'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Problems(IncrementalFreshserviceStream):
    object_name = 'problems'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Changes(IncrementalFreshserviceStream):
    object_name = 'changes'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Releases(IncrementalFreshserviceStream):
    object_name = 'releases'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Requesters(FullRefrehsFreshserviceStream):
    object_name = 'requesters'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Agents(FullRefrehsFreshserviceStream):
    object_name = 'agents'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Locations(FullRefrehsFreshserviceStream):
    object_name = 'locations'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Products(FullRefrehsFreshserviceStream):
    object_name = 'products'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Vendors(FullRefrehsFreshserviceStream):
    object_name = 'vendors'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Assets(FullRefrehsFreshserviceStream):
    object_name = 'assets'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class PurchaseOrders(FullRefrehsFreshserviceStream):
    object_name = 'purchase_orders'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name

class Software(FullRefrehsFreshserviceStream):
    object_name = 'applications'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self.object_name