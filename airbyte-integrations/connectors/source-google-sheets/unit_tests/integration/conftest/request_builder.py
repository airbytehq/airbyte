#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from airbyte_cdk.test.mock_http.request import HttpRequest


GOOGLE_SHEETS_BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"
OAUTH_AUTHORIZATION_ENDPOINT = "https://www.googleapis.com/oauth2/v4"


class RequestBuilder:
    @classmethod
    def get_account_endpoint(cls) -> RequestBuilder:
        return cls(resource="values:batchGet")

    def __init__(self, resource: str = None) -> None:
        self._spreadsheet_id = None
        self._query_params = {}
        self._body = None
        self.resource = resource

    def with_include_grid_data(self, include_grid_data: bool) -> RequestBuilder:
        self._query_params["includeGridData"] = "true" if include_grid_data else "false"
        return self

    def with_alt(self, alt: str) -> RequestBuilder:
        self._query_params["alt"] = alt
        return self

    def with_ranges(self, ranges: str) -> RequestBuilder:
        self._query_params["ranges"] = ranges
        return self

    def with_major_dimension(self, dimension: str) -> RequestBuilder:
        self._query_params["majorDimension"] = dimension
        return self

    def with_spreadsheet_id(self, spreadsheet_id: str) -> RequestBuilder:
        self._spreadsheet_id = spreadsheet_id
        return self

    def build(self) -> HttpRequest:
        endpoint = f"/{self.resource}" if self.resource else ""
        return HttpRequest(
            url=f"{GOOGLE_SHEETS_BASE_URL}/{self._spreadsheet_id}{endpoint}",
            query_params=self._query_params,
            body=self._body,
        )


class AuthBuilder:
    @classmethod
    def get_token_endpoint(cls) -> AuthBuilder:
        return cls(resource="token")

    def __init__(self, resource):
        self._body = ""
        self._resource = resource
        self._query_params = ""

    def with_body(self, body: str):
        self._body = body
        return self

    def build(self) -> HttpRequest:
        endpoint = f"/{self._resource}" if self._resource else ""
        return HttpRequest(
            url=f"{OAUTH_AUTHORIZATION_ENDPOINT}{endpoint}",
            query_params=self._query_params,
            body=self._body,
        )
