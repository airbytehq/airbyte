#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl, urlparse

import arrow
import requests

from airbyte_cdk.sources.streams.http import HttpStream
from source_tplcentral.util import deep_get, normalize


class TplcentralStream(HttpStream, ABC):
    url_base = None

    def __init__(self, config) -> None:
        super().__init__(authenticator=config["authenticator"])

        self.url_base = config["url_base"]
        self.customer_id = config.get("customer_id")
        self.facility_id = config.get("facility_id")
        self.start_date = config.get("start_date")

        self.total_results_field = "TotalResults"

    primary_key = "_id"

    @property
    def page_size(self):
        None

    @property
    def upstream_primary_key(self):
        None

    @property
    def upstream_cursor_field(self):
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

        pgsiz = int(qs.get("pgsiz", pgsiz))
        pgnum = int(qs.get("pgnum", 1))

        if pgsiz > 0 and pgsiz * pgnum < total:
            return {
                "pgsiz": pgsiz,
                "pgnum": pgnum + 1,
            }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = normalize(response.json()[self.collection_field])

        for record in records:
            if self.upstream_primary_key:
                record[self.primary_key] = deep_get(record, self.upstream_primary_key)
            if self.upstream_cursor_field:
                record[self.cursor_field] = deep_get(record, self.upstream_cursor_field)
            yield record


class StockSummaries(TplcentralStream):
    # https://api.3plcentral.com/rels/inventory/stocksummaries
    collection_field = "Summaries"
    primary_key = ["FacilityId", "_item_identifier_id"]
    page_size = 500

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "inventory/stocksummaries"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = super().parse_response(response, **kwargs)

        for record in records:
            record["_item_identifier_id"] = deep_get(record, "ItemIdentifier.Id")
            yield record


class Customers(TplcentralStream):
    # https://api.3plcentral.com/rels/customers/customers
    upstream_primary_key = "ReadOnly.CustomerId"
    collection_field = "ResourceList"
    page_size = 100

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "customers"


class IncrementalTplcentralStream(TplcentralStream, ABC):
    state_checkpoint_interval = 100

    cursor_field = "_cursor"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current = current_stream_state.get(self.cursor_field, "")
        latest = latest_record.get(self.cursor_field, "")

        if current and latest:
            return {self.cursor_field: max(arrow.get(latest), arrow.get(current)).datetime.replace(tzinfo=None).isoformat()}

        return {self.cursor_field: max(latest, current)}

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        if stream_state is None:
            stream_state = {}

        return [{self.cursor_field: stream_state.get(self.cursor_field, self.start_date)}]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        return params or {}


class Items(IncrementalTplcentralStream):
    # https://api.3plcentral.com/rels/customers/items
    upstream_primary_key = "ItemId"
    upstream_cursor_field = "ReadOnly.LastModifiedDate"
    collection_field = "ResourceList"
    page_size = 100

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

        params.update({"sort": self.upstream_cursor_field})
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update({"rql": f"{self.upstream_cursor_field}=ge={cursor}"})

        return params


class StockDetails(IncrementalTplcentralStream):
    # https://api.3plcentral.com/rels/inventory/stockdetails
    upstream_primary_key = "ReceiveItemId"
    upstream_cursor_field = "ReceivedDate"
    collection_field = "ResourceList"
    page_size = 500

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

        params.update(
            {
                "customerid": self.customer_id,
                "facilityid": self.facility_id,
                "sort": self.upstream_cursor_field,
            }
        )
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update({"rql": f"{self.upstream_cursor_field}=ge={cursor}"})

        return params


class Inventory(IncrementalTplcentralStream):
    # https://api.3plcentral.com/rels/inventory/inventory
    upstream_primary_key = "ReceiveItemId"
    upstream_cursor_field = "ReceivedDate"
    collection_field = "ResourceList"
    page_size = 1000

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

        params.update(
            {
                "sort": self.upstream_cursor_field,
                "rql": ";".join(
                    [
                        f"CustomerIdentifier.Id=={self.customer_id}",
                        f"FacilityIdentifier.Id=={self.facility_id}",
                    ]
                ),
            }
        )
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update(
                {
                    "rql": ";".join(
                        [
                            params["rql"],
                            f"{self.upstream_cursor_field}=ge={cursor}",
                        ]
                    )
                }
            )

        return params


class Orders(IncrementalTplcentralStream):
    # https://api.3plcentral.com/rels/orders/orders
    upstream_primary_key = "ReadOnly.OrderId"
    upstream_cursor_field = "ReadOnly.LastModifiedDate"
    collection_field = "ResourceList"
    page_size = 1000

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

        params.update(
            {
                "sort": self.upstream_cursor_field,
                "rql": ";".join(
                    [
                        f"ReadOnly.CustomerIdentifier.Id=={self.customer_id}",
                        f"ReadOnly.FacilityIdentifier.Id=={self.facility_id}",
                    ]
                ),
            }
        )
        cursor = stream_slice.get(self.cursor_field)
        if cursor:
            params.update(
                {
                    "rql": ";".join(
                        [
                            params["rql"],
                            f"{self.upstream_cursor_field}=ge={cursor}",
                        ]
                    )
                }
            )

        return params
