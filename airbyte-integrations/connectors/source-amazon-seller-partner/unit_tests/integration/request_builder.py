#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Optional

import pendulum
from airbyte_cdk.test.mock_http import HttpRequest


auth_request = HttpRequest(
    url="https://api.amazon.com/auth/o2/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    body={
        "grant_type": "refresh_token",
        "client_id": "self.client_id",
        "client_secret": "self.client_secret",
        "refresh_token": "self.refresh_token",
    }
)


class RequestBuilder(ABC):

    @classmethod
    def vendor_direct_fulfillment_shipping_endpoint(cls):
        return cls("vendor/directFulfillment/shipping/v1/shippingLabels")

    _ACCESS_TOKEN = "test_access_token"
    _BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    def __init__(self, resource: str) -> None:
        self._resource = resource

    @property
    def url(self) -> str:
        return ""

    @property
    def headers(self) -> Dict[str, Any]:
        return {
            "content-type": "application/json",
            "host": self._BASE_URL.replace("https://", ""),
            "user-agent": "python-requests",
            "x-amz-access-token": self._ACCESS_TOKEN,
            "x-amz-date": pendulum.now("utc").strftime("%Y%m%dT%H%M%SZ"),
        }

    @property
    def body(self) -> Optional[Dict[str, Any]]:
        return None

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self._BASE_URL}/{self.url}/{self._resource}",
            headers=self.headers,
            # TODO: uncomment when airbyte_cdk.test.mock_http is updated
            # body=self.body,
        )


class ReportBasedStreamRequestBuilder(RequestBuilder):

    @classmethod
    def create_report_endpoint(cls, report_name: str) -> ReportBasedStreamRequestBuilder:
        return cls("reports", report_name)

    @classmethod
    def check_report_status_endpoint(cls, report_name: str, report_id: str) -> ReportBasedStreamRequestBuilder:
        return cls(f"reports/{report_id}", report_name)

    @classmethod
    def get_document_download_url_endpoint(cls, report_name: str, document_id: str) -> ReportBasedStreamRequestBuilder:
        return cls(f"documents/{document_id}", report_name)

    @classmethod
    def download_document_endpoint(cls, report_name: str, document_id: str) -> ReportBasedStreamRequestBuilder:
        return cls(f"documents/{document_id}", report_name)

    # TODO: find a better place
    _MARKETPLACE_ID = "ATVPDKIKX0DER"

    url = "reports/2021-06-30"

    @property
    def body(self) -> Optional[Dict[str, Any]]:
        # TODO: need to pass stream slice or what? Maybe with_stream_slice method?
        return {"reportType": self._report_name, "marketplaceIds": [self._MARKETPLACE_ID], "dataStartTime": "", "dataEndTime": ""}

    def __init__(self, resource: str, report_name: str) -> None:
        super().__init__(resource)
        self._report_name = report_name
