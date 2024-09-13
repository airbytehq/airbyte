#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

import json
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest

from .config import ACCESS_TOKEN, LWA_APP_ID, LWA_CLIENT_SECRET, MARKETPLACE_ID, NOW, REFRESH_TOKEN


class RequestBuilder:
    @classmethod
    def auth_endpoint(cls) -> RequestBuilder:
        request_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        request_body = (
            f"grant_type=refresh_token&client_id={LWA_APP_ID}&" f"client_secret={LWA_CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}"
        )
        return cls("auth/o2/token").with_base_url("https://api.amazon.com").with_headers(request_headers).with_body(request_body)

    @classmethod
    def create_report_endpoint(cls, report_name: str) -> RequestBuilder:
        request_body = {
            "reportType": report_name,
            "marketplaceIds": [MARKETPLACE_ID],
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
        }
        return cls("reports/2021-06-30/reports").with_body(json.dumps(request_body))

    @classmethod
    def create_vendor_traffic_report_endpoint(cls, report_name: str) -> RequestBuilder:
        request_body = {
            "reportType": report_name,
            "marketplaceIds": [MARKETPLACE_ID],
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-01T23:59:59Z",
        }
        return cls("reports/2021-06-30/reports").with_body(json.dumps(request_body))

    @classmethod
    def check_report_status_endpoint(cls, report_id: str) -> RequestBuilder:
        return cls(f"reports/2021-06-30/reports/{report_id}")

    @classmethod
    def get_document_download_url_endpoint(cls, document_id: str) -> RequestBuilder:
        return cls(f"reports/2021-06-30/documents/{document_id}")

    @classmethod
    def download_document_endpoint(cls, url: str) -> RequestBuilder:
        return cls("").with_base_url(url).with_headers(None)

    @classmethod
    def vendor_direct_fulfillment_shipping_endpoint(cls) -> RequestBuilder:
        return cls("vendor/directFulfillment/shipping/v1/shippingLabels")

    @classmethod
    def vendor_orders_endpoint(cls) -> RequestBuilder:
        return cls("vendor/orders/v1/purchaseOrders")

    def __init__(self, resource: str) -> None:
        self._resource = resource
        self._base_url = "https://sellingpartnerapi-na.amazon.com"
        self._headers = {
            "content-type": "application/json",
            "host": self._base_url.replace("https://", ""),
            "user-agent": "python-requests",
            "x-amz-access-token": ACCESS_TOKEN,
            "x-amz-date": NOW.strftime("%Y%m%dT%H%M%SZ"),
        }
        self._query_params = ANY_QUERY_PARAMS
        self._body = None

    def with_base_url(self, base_url: str) -> RequestBuilder:
        self._base_url = base_url
        return self

    def with_headers(self, headers: Optional[Union[str, Mapping[str, str]]]) -> RequestBuilder:
        self._headers = headers
        return self

    def with_query_params(self, query_params: Union[str, Mapping[str, Union[str, List[str]]]]) -> RequestBuilder:
        self._query_params = query_params
        return self

    def with_body(self, body: Union[str, bytes, Mapping[str, Any]]) -> RequestBuilder:
        self._body = body
        return self

    def _url(self) -> str:
        return f"{self._base_url}/{self._resource}" if self._resource else self._base_url

    def build(self) -> HttpRequest:
        return HttpRequest(url=self._url(), query_params=self._query_params, headers=self._headers, body=self._body)
