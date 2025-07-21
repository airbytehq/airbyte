#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Union

from airbyte_cdk.test.mock_http.request import HttpRequest


CLIENT_CENTER_BASE_URL = "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13"
REPORTING_BASE_URL = "https://reporting.api.bingads.microsoft.com/Reporting/v13"
BULK_BASE_URL = "https://bulk.api.bingads.microsoft.com"
REPORT_URL = "https://bingadsappsstorageprod.blob.core.windows.net:443/dumb/testing/potato/AdPerformanceReport.zip?skoid=dubb&sktid=testing&skt=potato&ske=potato&sks=b&skv=2019-12-12&sv=2023-11-03&st=potato&se=potato&sr=b&sp=r&sig=potato"


class RequestBuilder:
    def __init__(self, resource: str = None, api="client_center") -> None:
        self._query_params = {}
        self._body = None
        self.resource = resource
        if api == "client_center":
            self._api = CLIENT_CENTER_BASE_URL
        elif api == "bulk":
            self._api = BULK_BASE_URL
        elif api == "reporting":
            self._api = REPORTING_BASE_URL
        else:
            raise Exception(f"Unsupported API request: {api}")

    def with_body(self, body: Union[str, bytes]):
        self._body = body
        return self

    def build(self) -> HttpRequest:
        endpoint = f"/{self.resource}" if self.resource else ""
        return HttpRequest(
            url=f"{self._api}{endpoint}",
            query_params=self._query_params,
            body=self._body,
        )

    def build_report_url(self) -> HttpRequest:
        return HttpRequest(
            url=REPORT_URL,
        )
