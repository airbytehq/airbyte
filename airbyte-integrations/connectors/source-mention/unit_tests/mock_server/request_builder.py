# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class MentionRequestBuilder:
    def __init__(self, path):
        self._path = path
        self._query_params = {}
        self._api_key = "test-api-key"

    @classmethod
    def account_me(cls):
        return cls("accounts/me")

    @classmethod
    def alerts(cls, account_id):
        return cls(f"accounts/{account_id}/alerts").with_query_param("limit", "100")

    def with_api_key(self, api_key):
        self._api_key = api_key
        return self

    def with_query_param(self, name, value):
        self._query_params[name] = value
        return self

    def build(self):
        return HttpRequest(
            url=f"https://api.mention.net/api/{self._path}",
            query_params=self._query_params,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
