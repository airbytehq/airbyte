# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest

from .config import SITE


# Must match manifest.yaml base URL exactly
API_BASE_URL = f"https://{SITE}.chargebee.com/api/v2"


class RequestBuilder:
    """Builder for creating HttpRequest objects for testing."""

    @classmethod
    def endpoint(cls, resource: str) -> "RequestBuilder":
        return cls(resource)

    @classmethod
    def customers_endpoint(cls) -> "RequestBuilder":
        return cls(resource="customers")

    @classmethod
    def customer_contacts_endpoint(cls, customer_id: str) -> "RequestBuilder":
        return cls(resource=f"customers/{customer_id}/contacts")

    @classmethod
    def subscriptions_endpoint(cls) -> "RequestBuilder":
        return cls(resource="subscriptions")

    @classmethod
    def invoices_endpoint(cls) -> "RequestBuilder":
        return cls(resource="invoices")

    @classmethod
    def events_endpoint(cls) -> "RequestBuilder":
        return cls(resource="events")

    @classmethod
    def transactions_endpoint(cls) -> "RequestBuilder":
        return cls(resource="transactions")

    @classmethod
    def plans_endpoint(cls) -> "RequestBuilder":
        return cls(resource="plans")

    @classmethod
    def addons_endpoint(cls) -> "RequestBuilder":
        return cls(resource="addons")

    @classmethod
    def coupons_endpoint(cls) -> "RequestBuilder":
        return cls(resource="coupons")

    @classmethod
    def items_endpoint(cls) -> "RequestBuilder":
        return cls(resource="items")

    @classmethod
    def item_attached_items_endpoint(cls, item_id: str) -> "RequestBuilder":
        return cls(resource=f"items/{item_id}/attached_items")

    @classmethod
    def gifts_endpoint(cls) -> "RequestBuilder":
        return cls(resource="gifts")

    @classmethod
    def credit_notes_endpoint(cls) -> "RequestBuilder":
        return cls(resource="credit_notes")

    def __init__(self, resource: str = "") -> None:
        self._resource = resource
        self._query_params: Dict[str, Any] = {}
        self._any_query_params = False

    def with_query_param(self, key: str, value: Any) -> "RequestBuilder":
        self._query_params[key] = value
        return self

    def with_limit(self, limit: int) -> "RequestBuilder":
        self._query_params["limit"] = str(limit)
        return self

    def with_offset(self, offset: str) -> "RequestBuilder":
        self._query_params["offset"] = offset
        return self

    def with_any_query_params(self) -> "RequestBuilder":
        """Use for endpoints with dynamic query params."""
        self._any_query_params = True
        return self

    def build(self) -> HttpRequest:
        query_params = ANY_QUERY_PARAMS if self._any_query_params else (self._query_params if self._query_params else None)
        return HttpRequest(
            url=f"{API_BASE_URL}/{self._resource}",
            query_params=query_params,
        )
