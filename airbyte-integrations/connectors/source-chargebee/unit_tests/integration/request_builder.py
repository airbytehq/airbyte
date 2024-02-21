# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import List, Optional

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class ChargebeeRequestBuilder:

    @classmethod
    def accounts_endpoint(cls, account_id: str, client_secret: str) -> "ChargebeeRequestBuilder":
        return cls("accounts", account_id, client_secret)

    @classmethod
    def items_endpoint(cls, account_id: str, client_secret: str) -> "ChargebeeRequestBuilder":
        return cls("v2/items", account_id, client_secret)

    @classmethod
    def _for_endpoint(cls, endpoint: str, account_id: str, client_secret: str) -> "ChargebeeRequestBuilder":
        return cls(endpoint, account_id, client_secret)

    def __init__(self, resource: str, account_id: str, client_secret: str) -> None:
        self._resource = resource
        self._account_id = account_id
        self._client_secret = client_secret
        self._any_query_params = False
        self._created_gte: Optional[datetime] = None
        self._created_lte: Optional[datetime] = None
        self._limit: Optional[int] = None
        self._object: Optional[str] = None
        self._starting_after_id: Optional[str] = None
        self._types: List[str] = []
        self._expands: List[str] = []

    def with_created_gte(self, created_gte: datetime) -> "ChargebeeRequestBuilder":
        self._created_gte = created_gte
        return self

    def with_created_lte(self, created_lte: datetime) -> "ChargebeeRequestBuilder":
        self._created_lte = created_lte
        return self

    def with_limit(self, limit: int) -> "ChargebeeRequestBuilder":
        self._limit = limit
        return self

    def with_object(self, object_name: str) -> "ChargebeeRequestBuilder":
        self._object = object_name
        return self

    def with_starting_after(self, starting_after_id: str) -> "ChargebeeRequestBuilder":
        self._starting_after_id = starting_after_id
        return self

    def with_any_query_params(self) -> "ChargebeeRequestBuilder":
        self._any_query_params = True
        return self

    def with_types(self, types: List[str]) -> "ChargebeeRequestBuilder":
        self._types = types
        return self

    def with_expands(self, expands: List[str]) -> "ChargebeeRequestBuilder":
        self._expands = expands
        return self

    def build(self) -> HttpRequest:
        query_params = {}
        if self._created_gte:
            query_params["created[gte]"] = str(int(self._created_gte.timestamp()))
        if self._created_lte:
            query_params["created[lte]"] = str(int(self._created_lte.timestamp()))
        if self._limit:
            query_params["limit"] = str(self._limit)
        if self._starting_after_id:
            query_params["starting_after"] = self._starting_after_id
        if self._types:
            query_params["types[]"] = self._types
        if self._object:
            query_params["object"] = self._object
        if self._expands:
            query_params["expand[]"] = self._expands

        if self._any_query_params:
            if query_params:
                raise ValueError(f"Both `any_query_params` and {list(query_params.keys())} were configured. Provide only one of none but not both.")
            query_params = ANY_QUERY_PARAMS

        return HttpRequest(
            url=f"https://api.stripe.com/v1/{self._resource}",
            query_params=query_params,
            headers={"Stripe-Account": self._account_id, "Authorization": f"Bearer {self._client_secret}"},
        )
