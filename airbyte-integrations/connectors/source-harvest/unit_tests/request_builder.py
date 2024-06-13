# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import base64
from datetime import datetime
from typing import List, Optional

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class HarvestRequestBuilder:

    @classmethod
    def invoices_endpoint(cls, account_id: str) -> "HarvestRequestBuilder":
        return cls("invoices", account_id)

    @classmethod
    def invoice_messages_endpoint(cls, account_id: str, invoice_id: str) -> "HarvestRequestBuilder":
        return cls(f"invoices/{invoice_id}/messages", account_id)

    @classmethod
    def expenses_clients_endpoint(cls, account_id: str) -> "HarvestRequestBuilder":
        return cls("reports/expenses/clients", account_id)

    def __init__(self, resource: str, account_id: str) -> "HarvestRequestBuilder":
        self._resource: str = resource
        self._account_id: str = account_id
        self._per_page: Optional[int] = None
        self._page: Optional[int] = None
        self._updated_since: Optional[str] = None
        self._from: Optional[str] = None
        self._to: Optional[str] = None
        self._any_query_params: bool = False


    def with_any_query_params(self) -> "HarvestRequestBuilder":
        self._any_query_params = True
        return self

    def with_per_page(self, per_page: int) -> "HarvestRequestBuilder":
        self._per_page = per_page
        return self

    def with_page(self, page: int) -> "HarvestRequestBuilder":
        self._page = page
        return self

    def with_updated_since(self, updated_since: str) -> "HarvestRequestBuilder":
        self._updated_since = updated_since
        return self

    def with_from(self, _from: datetime) -> "HarvestRequestBuilder":
        self._from = datetime.strftime(_from, "%Y%m%d")
        return self

    def with_to(self, to: datetime) -> "HarvestRequestBuilder":
        self._to = datetime.strftime(to, "%Y%m%d")
        return self

    def build(self) -> HttpRequest:
        query_params = {}
        if self._page:
            query_params["page"] = self._page
        if self._per_page:
            query_params["per_page"] = self._per_page
        if self._updated_since:
            query_params["updated_since"] = self._updated_since
        if self._from:
            query_params["from"] = self._from
        if self._to:
            query_params["to"] = self._to

        if self._any_query_params:
            if query_params:
                raise ValueError(f"Both `any_query_params` and {list(query_params.keys())} were configured. Provide only one of none but not both.")
            query_params = ANY_QUERY_PARAMS

        return HttpRequest(
            url=f"https://api.harvestapp.com/v2/{self._resource}",
            query_params=query_params,
            headers={}
        )