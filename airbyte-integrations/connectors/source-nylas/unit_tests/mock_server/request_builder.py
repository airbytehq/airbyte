# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class NylasRequestBuilder:
    def __init__(self, path):
        self._path = path
        self._query_params = {"limit": "50"}

    @classmethod
    def endpoint(cls, path):
        return cls(path)

    def with_query_param(self, name, value):
        self._query_params[name] = value
        return self

    def build(self):
        return HttpRequest(
            url=f"https://api.us.nylas.com/v3{self._path}",
            query_params=dict(self._query_params),
            headers={"Authorization": "Bearer test-api-key"},
        )
