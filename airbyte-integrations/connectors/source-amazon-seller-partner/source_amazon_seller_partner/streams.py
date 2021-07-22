#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from source_amazon_seller_partner.auth import AWSSigV4


class AspStream(HttpStream, ABC):
    page_size = 100
    data_field = "payload"

    def __init__(self, url_base: str, authenticator: AWSSigV4, access_token_credentials: dict, replication_start_date: str):
        self._url_base = url_base
        self._authenticator = authenticator
        self._access_token_credentials = access_token_credentials
        self._session = requests.Session()
        self._replication_start_date = replication_start_date

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    @abstractmethod
    def replication_start_date_field(self) -> str:
        pass

    @property
    @abstractmethod
    def next_page_token_field(self) -> str:
        pass

    @property
    @abstractmethod
    def page_size_field(self) -> str:
        pass

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return next_page_token

        params = {self.replication_start_date_field: self._replication_start_date, self.page_size_field: self.page_size}
        if self._replication_start_date:
            start_date = max(stream_state.get(self.cursor_field, self._replication_start_date), self._replication_start_date)
            params.update({self.replication_start_date_field: start_date})
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get("nextToken")
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field, [])
        yield from records

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def _get_access_token(self) -> str:
        """
        Get's the access token
        :return: access_token str
        """
        data = {"grant_type": "refresh_token", **self._access_token_credentials}
        headers = {"User-Agent": "python-sp-api-0.6.2", "content-type": "application/x-www-form-urlencoded;charset=UTF-8"}
        res = requests.post("https://api.amazon.com/auth/o2/token", data, headers)
        return res.json()["access_token"]

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "host": "sellingpartnerapi-na.amazon.com",
            "user-agent": "python-sp-api-0.6.2",
            "x-amz-access-token": self._get_access_token(),
            "x-amz-date": pendulum.now("utc").strftime("%Y%m%dT%H%M%SZ"),
            "content-type": "application/json",
        }

    def _create_prepared_request(
        self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None, auth: AWSSigV4 = None
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": self.url_base + path, "headers": headers, "params": params, "auth": auth}

        if self.http_method.upper() == "POST":
            args["json"] = json

        return self._session.prepare_request(requests.Request(**args))

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False

        next_page_token = None
        while not pagination_complete:
            request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            request = self._create_prepared_request(
                path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                headers=dict(request_headers),
                params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                auth=self.authenticator,
            )
            request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            response = self._send_request(request, request_kwargs)
            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []


class RecordsBase(AspStream, ABC):
    primary_key = "reportId"
    cursor_field = "createdTime"
    replication_start_date_field = "createdSince"
    next_page_token_field = "nextToken"
    page_size_field = "pageSize"

    def path(self, **kwargs):
        return "/reports/2020-09-04/reports"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token, **kwargs)
        if not next_page_token:
            params.update({"reportTypes": self.name})
        return params


class MerchantListingsReports(RecordsBase):
    name = "GET_MERCHANT_LISTINGS_ALL_DATA"


class FlatFileOrdersReports(RecordsBase):
    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"


class FbaInventoryReports(RecordsBase):
    name = "GET_FBA_INVENTORY_AGED_DATA"


class Orders(AspStream):
    name = "Orders"
    primary_key = "AmazonOrderId"
    cursor_field = "LastUpdateDate"
    replication_start_date_field = "LastUpdatedAfter"
    next_page_token_field = "NextToken"
    page_size_field = "MaxResultsPerPage"

    def __init__(self, marketplace_ids, **kwargs):
        super().__init__(**kwargs)
        self.marketplace_ids = marketplace_ids

    def path(self, **kwargs):
        return "/orders/v0/orders"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token, **kwargs)
        if not next_page_token:
            params.update({"MarketplaceIds": self.marketplace_ids})
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field, {}).get(self.name, [])
        yield from records
