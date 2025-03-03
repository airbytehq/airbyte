#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
import vcr
from requests.auth import AuthBase
from vcr.cassette import Cassette

from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator


class LinnworksStream(HttpStream, ABC):
    http_method = "POST"

    def __init__(self, authenticator: Union[AuthBase, HttpAuthenticator] = None, start_date: str = None):
        super().__init__(authenticator=authenticator)

        self._authenticator = authenticator
        self.start_date = start_date

    @property
    def url_base(self) -> str:
        return self._session.auth.get_server()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json = response.json()
        if not isinstance(json, list):
            json = [json]
        for record in json:
            yield record

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)


class LinnworksGenericPagedResult(ABC):
    # https://apps.linnworks.net/Api/Class/linnworks-spa-commondata-Generic-GenericPagedResult
    @abstractmethod
    def paged_result(self, response: requests.Response) -> Mapping[str, Any]:
        pass

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        result = self.paged_result(response)

        if result["PageNumber"] < result["TotalPages"]:
            return {
                "PageNumber": result["PageNumber"] + 1,
                "EntriesPerPage": result["EntriesPerPage"],
                "TotalEntries": result["TotalEntries"],
                "TotalPages": result["TotalPages"],
            }


class StockLocations(LinnworksStream):
    # https://apps.linnworks.net/Api/Method/Inventory-GetStockLocations
    # Response: List<StockLocation> https://apps.linnworks.net/Api/Class/linnworks-spa-commondata-Inventory-ClassBase-StockLocation
    # Allows 150 calls per minute
    primary_key = "StockLocationIntId"
    use_cache = True

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/api/Inventory/GetStockLocations"


class StockLocationDetails(HttpSubStream, StockLocations):
    # https://apps.linnworks.net/Api/Method/Locations-GetLocation
    # Response: StockLocation https://apps.linnworks.net/Api/Class/linnworks-spa-commondata-Locations-ClassBase-StockLocation
    # Allows 150 calls per minute
    primary_key = "StockLocationIntId"

    def __init__(self, **kwargs):
        super().__init__(StockLocations(**kwargs), **kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/api/Locations/GetLocation"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any], **kwargs) -> MutableMapping[str, Any]:
        return {"pkStockLocationId ": stream_slice["parent"]["StockLocationId"]}


class StockItems(LinnworksStream):
    # https://apps.linnworks.net//Api/Method/Stock-GetStockItemsFull
    # Response: List<StockItemFull> https://apps.linnworks.net/Api/Class/linnworks-spa-commondata-Inventory-ClassBase-StockItemFull
    # Allows 250 calls per minute
    primary_key = "StockItemIntId"
    page_size = 200

    raise_on_http_errors = False

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/api/Stock/GetStockItemsFull"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        url = urlparse(response.request.url)
        qs = dict(parse_qsl(url.query))

        page_size = int(qs.get("entriesPerPage", self.page_size))
        page_number = int(qs.get("pageNumber", 0))

        data = response.json()

        if response.status_code == requests.codes.ok and len(data) == page_size:
            return {
                "entriesPerPage": page_size,
                "pageNumber": page_number + 1,
            }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == requests.codes.bad_request:
            return None
        response.raise_for_status()
        yield from super().parse_response(response, **kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "entriesPerPage": self.page_size,
            "pageNumber": 1,
            "loadCompositeParents": "true",
            "loadVariationParents": "true",
            "dataRequirements": "[0,1,2,3,4,5,6,7,8]",
            "searchTypes": "[0,1,2]",
        }

        if next_page_token:
            params.update(next_page_token)

        return params


class IncrementalLinnworksStream(LinnworksStream, ABC):
    @property
    def cursor_field(self) -> str:
        return True

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current = current_stream_state.get(self.cursor_field, "")
        latest = latest_record.get(self.cursor_field, "")

        return {
            self.cursor_field: max(latest, current),
        }


class ProcessedOrders(LinnworksGenericPagedResult, IncrementalLinnworksStream):
    # https://apps.linnworks.net/Api/Method/ProcessedOrders-SearchProcessedOrders
    # Response: SearchProcessedOrdersResponse https://apps.linnworks.net/Api/Class/API_Linnworks-Controllers-ProcessedOrders-Responses-SearchProcessedOrdersResponse
    # Allows 150 calls per minute
    primary_key = "nOrderId"
    cursor_field = "dProcessedOn"
    page_size = 500
    use_cache = True

    def path(self, **kwargs) -> str:
        return "/api/ProcessedOrders/SearchProcessedOrders"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        if not stream_state:
            stream_state = {}

        from_date = pendulum.parse(stream_state.get(self.cursor_field, self.start_date))
        end_date = max(from_date, pendulum.tomorrow("UTC"))

        date_diff = end_date - from_date
        if date_diff.years > 0:
            interval = pendulum.duration(months=1)
        elif date_diff.months > 0:
            interval = pendulum.duration(weeks=1)
        elif date_diff.weeks > 0:
            interval = pendulum.duration(days=1)
        else:
            interval = pendulum.duration(hours=1)

        while True:
            to_date = min(from_date + interval, end_date)
            yield {"FromDate": from_date.isoformat(), "ToDate": to_date.isoformat()}
            from_date = to_date
            if from_date >= end_date:
                break

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        request = {
            "DateField": "processed",
            "FromDate": stream_slice["FromDate"],
            "ToDate": stream_slice["ToDate"],
            "PageNumber": 1 if not next_page_token else next_page_token["PageNumber"],
            "ResultsPerPage": self.page_size,
            "SearchSorting": {"SortField": "dProcessedOn", "SortDirection": "ASC"},
        }

        return {
            "request": json.dumps(request, separators=(",", ":")),
        }

    def paged_result(self, response: requests.Response) -> Mapping[str, Any]:
        return response.json()["ProcessedOrders"]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in self.paged_result(response)["Data"]:
            yield record

    def request_cache(self) -> Cassette:
        try:
            os.remove(self.cache_filename)
        except FileNotFoundError:
            pass

        return vcr.use_cassette(
            self.cache_filename,
            record_mode="new_episodes",
            serializer="yaml",
            match_on=["method", "scheme", "host", "port", "path", "query", "body"],
        )


class ProcessedOrderDetails(HttpSubStream, IncrementalLinnworksStream):
    # https://apps.linnworks.net/Api/Method/Orders-GetOrdersById
    # Response: List<OrderDetails> https://apps.linnworks.net/Api/Class/linnworks-spa-commondata-OrderManagement-ClassBase-OrderDetails
    # Allows 250 calls per minute
    primary_key = "NumOrderId"
    cursor_field = "ProcessedDateTime"
    page_size = 100

    def __init__(self, **kwargs):
        super().__init__(ProcessedOrders(**kwargs), **kwargs)

    def path(self, **kwargs) -> str:
        return "/api/Orders/GetOrdersById"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        parent_stream_state = None
        if stream_state:
            parent_stream_state = {"dProcessedOn": stream_state["ProcessedDateTime"]}

        buffer = []
        for slice in HttpSubStream.stream_slices(self, stream_state=parent_stream_state, **kwargs):
            buffer.append(slice["parent"]["pkOrderID"])
            if len(buffer) == self.page_size:
                yield buffer
                buffer = []
        if len(buffer) > 0:
            yield buffer

    def request_body_data(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "pkOrderIds": json.dumps(stream_slice, separators=(",", ":")),
        }
