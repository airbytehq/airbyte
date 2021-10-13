from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl, urlparse
from airbyte_cdk.sources.utils.casing import camel_to_snake

import arrow
import requests
from airbyte_cdk.sources.streams.http import HttpStream

from source_tplcentral.util import normalize


class TplcentralStream(HttpStream, ABC):
    url_base = None

    def __init__(self, config) -> None:
        super().__init__(authenticator=config['authenticator'])

        self.url_base = config['url_base']
        self.customer_id = config.get('customer_id')
        self.facility_id = config.get('facility_id')
        self.start_date = config.get('start_date')

        self.total_results_field = "TotalResults"

    @property
    def page_size(self):
        None

    @property
    @abstractmethod
    def collection_field(self) -> str:
        pass

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        data = response.json()
        total = data[self.total_results_field]

        pgsiz = self.page_size or len(data[self.collection_field])

        url = urlparse(response.request.url)
        qs = dict(parse_qsl(url.query))

        pgsiz = int(qs.get('pgsiz', pgsiz))
        pgnum = int(qs.get('pgnum', 1))

        if pgsiz * pgnum <= total:
            return {
                'pgsiz': pgsiz,
                'pgnum': pgnum + 1,
            }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return normalize(response.json()[self.collection_field])


class StockSummaries(TplcentralStream):
    collection_field = "Summaries"
    primary_key = ["facility_id", ["item_identifier", "id"]]
    page_size = 500

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "inventory/stocksummaries"


class Customers(TplcentralStream):
    collection_field = "ResourceList"
    primary_key = [["read_only", "customer_id"]]
    page_size = 100

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "customers"


class IncrementalTplcentralStream(TplcentralStream, ABC):
    state_checkpoint_interval = 10

    @staticmethod
    @abstractmethod
    def cursor_value(self) -> str:
        pass

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """

        current = current_stream_state.get(self.cursor_field)
        latest = latest_record.get(self.cursor_field)

        if current:
            return {self.cursor_field: max(arrow.get(latest), arrow.get(current)).isoformat()}

        return {self.cursor_field: self.start_date}

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        return [{
            self.cursor_field: stream_state.get(self.cursor_field, self.start_date)
        }]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        return params or {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response = super().parse_response(response, **kwargs)
        return [{
            **record,
            self.cursor_field: self.__class__.cursor_value(record)
        } for record in response]


class Items(IncrementalTplcentralStream):
    cursor_field = "cursor"
    collection_field = "ResourceList"

    primary_key = "cursor"

    @staticmethod
    def cursor_value(record) -> str:
        return record["read_only"]["last_modified_date"]

    def path(self, **kwargs) -> str:
        return f"customers/{self.customer_id}/items"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        params.update({"sort": "ReadOnly.LastModifiedDate"})
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update({"rql": f"ReadOnly.LastModifiedDate=ge={cursor}"})

        return params


class StockDetails(IncrementalTplcentralStream):
    cursor_field = "cursor"
    collection_field = "ResourceList"

    primary_key = "cursor"

    @staticmethod
    def cursor_value(record) -> str:
        return record["received_date"]

    def path(self, **kwargs) -> str:
        return "inventory/stockdetails"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        params.update({
            "customerid": self.customer_id,
            "facilityid": self.facility_id,
            "sort": "ReceivedDate",
        })
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update({"rql": f"ReceivedDate=ge={cursor}"})

        return params


class Inventory(IncrementalTplcentralStream):
    cursor_field = "cursor"
    collection_field = "ResourceList"

    primary_key = "cursor"

    @staticmethod
    def cursor_value(record) -> str:
        return record["received_date"]

    def path(self, **kwargs) -> str:
        return "inventory"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        params.update({
            "sort": "ReceivedDate",
            "rql": ";".join([
                f"CustomerIdentifier.Id=={self.customer_id}",
                f"FacilityIdentifier.Id=={self.facility_id}",
            ])
        })
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update({
                "rql": ";".join([
                    params["rql"],
                    f"ReceivedDate=ge={cursor}",
                ])
            })

        return params


class Orders(IncrementalTplcentralStream):
    cursor_field = "cursor"
    collection_field = "ResourceList"

    primary_key = "cursor"

    @staticmethod
    def cursor_value(record) -> str:
        return record["read_only"]["last_modified_date"]

    def path(self, **kwargs) -> str:
        return "orders"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        params.update({
            "sort": "ReadOnly.LastModifiedDate",
            "rql": ";".join([
                f"ReadOnly.CustomerIdentifier.Id=={self.customer_id}",
                f"ReadOnly.FacilityIdentifier.Id=={self.facility_id}",
            ])
        })
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update({
                "rql": ";".join([
                    params["rql"],
                    f"ReadOnly.LastModifiedDate=ge={cursor}",
                ])
            })

        return params
