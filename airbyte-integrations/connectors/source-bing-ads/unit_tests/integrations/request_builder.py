#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Union

from airbyte_cdk.test.mock_http.request import HttpRequest


CLIENT_CENTER_BASE_URL = "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13"


class RequestBuilder:
    def __init__(self, resource: str = None) -> None:
        self._spreadsheet_id = None
        self._query_params = {}
        self._body = None
        self.resource = resource

    def with_body(self, body: Union[str, bytes]):
        self._body = body
        return self

    def build(self) -> HttpRequest:
        endpoint = f"/{self.resource}" if self.resource else ""
        return HttpRequest(
            url=f"{CLIENT_CENTER_BASE_URL}{endpoint}",
            query_params=self._query_params,
            body=self._body,
        )
