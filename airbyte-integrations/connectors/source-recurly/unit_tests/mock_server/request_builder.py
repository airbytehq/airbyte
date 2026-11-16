# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

from airbyte_cdk.test.mock_http import HttpRequest


API_BASE_URL = "https://v3.recurly.com"


class RequestBuilder:
    def __init__(self, path: str) -> None:
        self._path = path
        self._params: dict[str, str] = {}

    @classmethod
    def endpoint(cls, path: str) -> "RequestBuilder":
        return cls(path)

    def with_query_params(self, **params: str) -> "RequestBuilder":
        self._params.update(params)
        return self

    @property
    def url(self) -> str:
        query = f"?{urlencode(self._params)}" if self._params else ""
        return f"{API_BASE_URL}/{self._path.lstrip('/')}" + query

    def build(self) -> HttpRequest:
        return HttpRequest(url=self.url)
