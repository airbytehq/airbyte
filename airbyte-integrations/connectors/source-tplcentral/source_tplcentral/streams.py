from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl, urlparse

import arrow
import requests
from airbyte_cdk.sources.streams.http import HttpStream

from source_tplcentral.util import normalize


class TplcentralStream(HttpStream, ABC):
    url_base = None

    def __init__(self, config) -> None:
        super().__init__(authenticator=config['authenticator'])

        self.url_base = config['url_base']
        self.customer_id = config.get('customer_id', None)
        self.facility_id = config.get('facility_id', None)
        self.start_date = config.get('start_date', None)

        if self.start_date is not None:
            self.start_date = arrow.get(self.start_date)

        self.total_results_field = "TotalResults"

    @property
    def page_size(self):
        None

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        data = response.json()
        total = data[self.total_results_field]

        pgsiz = self.page_size or len(data[self.collection_field])

        url = urlparse(response.request.url)
        qs = dict(parse_qsl(url.query))

        pgsiz = int(qs.get('pgsiz', pgsiz))
        pgnum = int(qs.get('pgnum', 1))

        if pgsiz * pgnum >= total:
            return None

        return {
            'pgsiz': pgsiz,
            'pgnum': pgnum + 1,
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class StockSummaries(TplcentralStream):
    primary_key = ["facility_id", ["item_identifier", "id"]]
    page_size = 500
    collection_field = "Summaries"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "inventory/stocksummaries"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [normalize(v) for v in response.json()['Summaries']]


class Customers(TplcentralStream):
    primary_key = [["read_only", "customer_id"]]
    page_size = 100

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "customers"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [normalize(v) for v in response.json()['ResourceList']]

class IncrementalTplcentralStream(TplcentralStream, ABC):
    state_checkpoint_interval = 10

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state is not None and "cursor" in current_stream_state:
            current_date = arrow.get(current_stream_state["cursor"])
            latest_record_date = arrow.get(latest_record["cursor"])
            return {
                "cursor": max(current_date, latest_record_date).isoformat()
            }
        return {
            "cursor": self.start_date.isoformat()
        }


class Items(IncrementalTplcentralStream):
    primary_key = "cursor"
    cursor_field = "cursor"

    collection_field = "ResourceList"

    def path(self, **kwargs) -> str:
        return f"customers/{self.customer_id}/items"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = arrow.get(stream_state["cursor"]) if stream_state and "date" in stream_state else self.start_date
        return [{
            "cursor": start_date
        }]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = next_page_token.copy() if isinstance(next_page_token, dict) else {}

        if self.cursor_field:
            cursor = stream_slice.get(self.cursor_field, None)
            if cursor:
                params.update({
                    "sort": "ReadOnly.LastModifiedDate",
                    "rql": f"ReadOnly.LastModifiedDate=ge={cursor}",
                })

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        out = []
        for v in response.json()['ResourceList']:
            v = normalize(v)
            v['cursor'] = v['read_only']['last_modified_date']
            out.append(v)
        return out


class StockDetails(IncrementalTplcentralStream):
    primary_key = "cursor"
    cursor_field = "cursor"

    collection_field = "ResourceList"

    def path(self, **kwargs) -> str:
        return "inventory/stockdetails"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = arrow.get(
            stream_state["cursor"]) if stream_state and "date" in stream_state else self.start_date
        return [{
            "cursor": start_date
        }]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = next_page_token.copy() if isinstance(next_page_token, dict) else {}

        if self.cursor_field:
            cursor = stream_slice.get(self.cursor_field, None)
            if cursor:
                params.update({
                    "customerid": self.customer_id,
                    "facilityid": self.facility_id,
                    "sort": "ReceivedDate",
                    "rql": f"ReceivedDate=ge={cursor}",
                })

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        out = []
        for v in response.json()['ResourceList']:
            v = normalize(v)
            v['cursor'] = v['received_date']
            out.append(v)
        return out


class Inventory(IncrementalTplcentralStream):
    primary_key = "cursor"
    cursor_field = "cursor"

    collection_field = "ResourceList"

    def path(self, **kwargs) -> str:
        return "inventory"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = arrow.get(
            stream_state["cursor"]) if stream_state and "date" in stream_state else self.start_date
        return [{
            "cursor": start_date
        }]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = next_page_token.copy() if isinstance(next_page_token, dict) else {}

        if self.cursor_field:
            cursor = stream_slice.get(self.cursor_field, None)
            if cursor:
                params.update({
                    "sort": "ReceivedDate",
                    "rql": ";".join([
                        f"ReceivedDate=ge={cursor}",
                        f"CustomerIdentifier.Id=={self.customer_id}",
                        f"FacilityIdentifier.Id=={self.facility_id}",
                    ])
                })

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        out = []
        for v in response.json()['ResourceList']:
            v = normalize(v)
            v['cursor'] = v['received_date']
            out.append(v)
        return out


class Orders(IncrementalTplcentralStream):
    primary_key = "cursor"
    cursor_field = "cursor"

    collection_field = "ResourceList"

    def path(self, **kwargs) -> str:
        return "orders"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = arrow.get(
            stream_state["cursor"]) if stream_state and "date" in stream_state else self.start_date
        return [{
            "cursor": start_date
        }]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = next_page_token.copy() if isinstance(next_page_token, dict) else {}

        if self.cursor_field:
            cursor = stream_slice.get(self.cursor_field, None)
            if cursor:
                params.update({
                    "sort": "ReadOnly.LastModifiedDate",
                    "rql": ";".join([
                        f"ReadOnly.LastModifiedDate=ge={cursor}",
                        f"ReadOnly.CustomerIdentifier.Id=={self.customer_id}",
                        f"ReadOnly.FacilityIdentifier.Id=={self.facility_id}",
                    ])
                })

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        out = []
        for v in response.json()['ResourceList']:
            v = normalize(v)
            v['cursor'] = v['read_only']['last_modified_date']
            out.append(v)
        return out
