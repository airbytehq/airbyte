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

import json as json_lib
import time
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from source_amazon_seller_partner.auth import AWSSignature

REPORTS_API_VERSION = "2020-09-04"
ORDERS_API_VERSION = "v0"


class AmazonSPStream(HttpStream, ABC):
    data_field = "payload"

    def __init__(
        self, url_base: str, aws_signature: AWSSignature, replication_start_date: str, marketplace_ids: List[str], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._url_base = url_base
        self._aws_signature = aws_signature
        self._replication_start_date = replication_start_date
        self.marketplace_ids = marketplace_ids

    @property
    def url_base(self) -> str:
        return self._url_base

    def _create_prepared_request(
        self, path: str, method: str = None, headers: Mapping = None, params: Mapping = None, json: Any = None, data: Any = None
    ) -> requests.PreparedRequest:
        """
        Override to prepare request for AWS API.
        AWS signature flow require prepared request to correctly generate `authorization` header.
        Add `auth` arg to sign all the requests with AWS signature.
        """
        http_method = method or self.http_method
        args = {"method": http_method, "url": self.url_base + path, "headers": headers, "params": params, "auth": self._aws_signature}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        return {"content-type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class IncrementalAmazonSPStream(AmazonSPStream, ABC):
    page_size = 100

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

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        pass

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return dict(next_page_token)

        params = {self.replication_start_date_field: self._replication_start_date, self.page_size_field: self.page_size}
        if self._replication_start_date:
            start_date = max(stream_state.get(self.cursor_field, self._replication_start_date), self._replication_start_date)
            params.update({self.replication_start_date_field: start_date})
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        next_page_token = stream_data.get(self.next_page_token_field)
        if next_page_token:
            return {self.next_page_token_field: next_page_token}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json().get(self.data_field, [])

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class ReportsAmazonSPStream(AmazonSPStream, ABC):
    primary_key = "reportId"
    path_prefix = f"/reports/{REPORTS_API_VERSION}/reports"
    wait_seconds = 30

    def should_retry(self, response: requests.Response) -> bool:
        should_retry = super().should_retry(response)
        if not should_retry:
            should_retry = response.json().get(self.data_field, {}).get("processingStatus") in ["IN_QUEUE", "IN_PROGRESS"]
        return should_retry

    def backoff_time(self, response: requests.Response):
        return self.wait_seconds

    def _create_report(self, stream_state: Mapping[str, Any] = None) -> Mapping[str, Any]:
        request_headers = self.request_headers(stream_state=stream_state)
        report_data = {"reportType": self.name, "marketplaceIds": self.marketplace_ids}
        create_report_request = self._create_prepared_request(
            method="POST",
            path=self.path_prefix,
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            data=json_lib.dumps(report_data),
        )
        report_response = self._send_request(create_report_request, {})

        time.sleep(self.wait_seconds)

        return report_response.json()[self.data_field]

    def path(self, stream_state: Mapping[str, Any] = None, **kwargs):
        return f"{self.path_prefix}/{self._create_report(stream_state)[self.primary_key]}"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield response.json().get(self.data_field, {})


class MerchantListingsReports(ReportsAmazonSPStream):
    name = "GET_MERCHANT_LISTINGS_ALL_DATA"


class FlatFileOrdersReports(ReportsAmazonSPStream):
    name = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"


class FbaInventoryReports(ReportsAmazonSPStream):
    name = "GET_FBA_INVENTORY_AGED_DATA"


class Orders(IncrementalAmazonSPStream):
    name = "Orders"
    primary_key = "AmazonOrderId"
    cursor_field = "LastUpdateDate"
    replication_start_date_field = "LastUpdatedAfter"
    next_page_token_field = "NextToken"
    page_size_field = "MaxResultsPerPage"

    def path(self, **kwargs):
        return f"/orders/{ORDERS_API_VERSION}/orders"

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token, **kwargs)
        if not next_page_token:
            params.update({"MarketplaceIds": ",".join(self.marketplace_ids)})
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json().get(self.data_field, {}).get(self.name, [])
