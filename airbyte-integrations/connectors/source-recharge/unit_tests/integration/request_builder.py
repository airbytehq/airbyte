#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from __future__ import annotations

import datetime as dt
from typing import Any, MutableMapping

from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import ACCESS_TOKEN, DATE_TIME_FORMAT


def get_stream_request(stream_name: str) -> RequestBuilder:
    return RequestBuilder.get_endpoint(stream_name).with_limit(250)


class RequestBuilder:
    @classmethod
    def get_endpoint(cls, endpoint: str) -> RequestBuilder:
        return cls(endpoint=endpoint)

    def __init__(self, endpoint: str) -> None:
        self._endpoint: str = endpoint
        self._query_params: MutableMapping[str, Any] = {}
        self._headers: MutableMapping[str, str] = {"X-Recharge-Version": "2021-11"}

    def with_limit(self, limit: int) -> RequestBuilder:
        self._query_params["limit"] = limit
        return self

    def with_updated_at_min(self, value: str) -> RequestBuilder:
        self._query_params["updated_at_min"] = dt.datetime.strptime(value, DATE_TIME_FORMAT).strftime(DATE_TIME_FORMAT)
        self._query_params["sort_by"] = "updated_at-asc"
        return self

    def with_next_page_token(self, next_page_token: str) -> RequestBuilder:
        self._query_params["cursor"] = next_page_token
        return self

    def with_access_token(self, access_token: str) -> RequestBuilder:
        self._headers["X-Recharge-Access-Token"] = access_token
        return self

    def with_old_api_version(self, api_version: str) -> RequestBuilder:
        self._headers["X-Recharge-Version"] = api_version
        return self

    def with_created_min(self, value: str) -> RequestBuilder:
        self._query_params["created_at_min"] = dt.datetime.strptime(value, DATE_TIME_FORMAT).strftime(DATE_TIME_FORMAT)
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.rechargeapps.com/{self._endpoint}",
            query_params=self._query_params,
            headers=self._headers,
        )
