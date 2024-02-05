# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import List, Optional

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class GithubRequestBuilder:

    @classmethod
    def events_endpoint(cls, repo: str, token: str) -> "GithubRequestBuilder":
        return cls(f"repos/{repo}/events", token)

    def __init__(self, resource: str, token: str) -> None:
        self._resource = resource
        self._token = token
        self._limit: Optional[int] = None

    def with_limit(self, limit: int) -> "GithubRequestBuilder":
        self._limit = limit
        return self

    def build(self) -> HttpRequest:
        query_params = {}
        # if self._created_gte:
        #     query_params["created[gte]"] = str(int(self._created_gte.timestamp()))
        # if self._created_lte:
        #     query_params["created[lte]"] = str(int(self._created_lte.timestamp()))
        # if self._limit:
        #     query_params["limit"] = str(self._limit)
        # if self._starting_after_id:
        #     query_params["starting_after"] = self._starting_after_id
        # if self._types:
        #     query_params["types[]"] = self._types
        # if self._object:
        #     query_params["object"] = self._object
        # if self._expands:
        #     query_params["expand[]"] = self._expands
        #
        # if self._any_query_params:
        #     if query_params:
        #         raise ValueError(f"Both `any_query_params` and {list(query_params.keys())} were configured. Provide only one of none but not both.")
        #     query_params = ANY_QUERY_PARAMS

        return HttpRequest(
            url=f"https://api.github.com/{self._resource}",
            query_params=query_params,
            headers={"Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "Authorization": f"Bearer {self._token}"},
        )