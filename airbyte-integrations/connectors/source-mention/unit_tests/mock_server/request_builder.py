# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class MentionRequestBuilder:
    def __init__(self, path, api_key):
        self._path = path
        self._api_key = api_key

    @classmethod
    def account_me_endpoint(cls, api_key):
        return cls("/accounts/me", api_key)

    def build(self):
        return HttpRequest(
            url=f"https://api.mention.net/api{self._path}",
            query_params={},
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
