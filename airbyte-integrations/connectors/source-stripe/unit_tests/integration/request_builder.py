# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from typing import List, Optional

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class StripeRequestBuilder:
    @classmethod
    def accounts_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("accounts", account_id, client_secret)

    @classmethod
    def application_fees_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("application_fees", account_id, client_secret)

    @classmethod
    def application_fees_refunds_endpoint(cls, application_fee_id: str, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls(f"application_fees/{application_fee_id}/refunds", account_id, client_secret)

    @classmethod
    def balance_transactions_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("balance_transactions", account_id, client_secret)

    @classmethod
    def customers_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("customers", account_id, client_secret)

    @classmethod
    def customers_bank_accounts_endpoint(cls, customer_id: str, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls(f"customers/{customer_id}/bank_accounts", account_id, client_secret)

    @classmethod
    def events_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("events", account_id, client_secret)

    @classmethod
    def external_accounts_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls(f"accounts/{account_id}/external_accounts", account_id, client_secret)

    @classmethod
    def issuing_authorizations_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("issuing/authorizations", account_id, client_secret)

    @classmethod
    def issuing_cards_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("issuing/cards", account_id, client_secret)

    @classmethod
    def issuing_transactions_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("issuing/transactions", account_id, client_secret)

    @classmethod
    def payment_methods_endpoint(cls, customer_id: str, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls(f"customers/{customer_id}/payment_methods", account_id, client_secret)

    @classmethod
    def payouts_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("payouts", account_id, client_secret)

    @classmethod
    def persons_endpoint(
        cls,
        parent_account_id: str,
        account_id: str,
        client_secret: str,
    ) -> "StripeRequestBuilder":
        return cls(f"accounts/{parent_account_id}/persons", account_id, client_secret)

    @classmethod
    def radar_early_fraud_warnings_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("radar/early_fraud_warnings", account_id, client_secret)

    @classmethod
    def reviews_endpoint(cls, account_id: str, client_secret: str) -> "StripeRequestBuilder":
        return cls("reviews", account_id, client_secret)

    @classmethod
    def _for_endpoint(cls, endpoint: str, account_id: str, client_secret: str) -> "StripeRequestBuilder":
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
        self._payout: Optional[str] = None
        self._starting_after_id: Optional[str] = None
        self._types: List[str] = []
        self._expands: List[str] = []

    def with_created_gte(self, created_gte: datetime) -> "StripeRequestBuilder":
        self._created_gte = created_gte
        return self

    def with_created_lte(self, created_lte: datetime) -> "StripeRequestBuilder":
        self._created_lte = created_lte
        return self

    def with_limit(self, limit: int) -> "StripeRequestBuilder":
        self._limit = limit
        return self

    def with_object(self, object_name: str) -> "StripeRequestBuilder":
        self._object = object_name
        return self

    def with_starting_after(self, starting_after_id: str) -> "StripeRequestBuilder":
        self._starting_after_id = starting_after_id
        return self

    def with_any_query_params(self) -> "StripeRequestBuilder":
        self._any_query_params = True
        return self

    def with_types(self, types: List[str]) -> "StripeRequestBuilder":
        self._types = types
        return self

    def with_expands(self, expands: List[str]) -> "StripeRequestBuilder":
        self._expands = expands
        return self

    def with_payout(self, payout: str) -> "StripeRequestBuilder":
        self._payout = payout
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
            if len(self._types) > 1:
                query_params["types[]"] = self._types
            else:
                query_params["type"] = self._types
        if self._object:
            query_params["object"] = self._object
        if self._payout:
            query_params["payout"] = self._payout
        if self._expands:
            query_params["expand[]"] = self._expands

        if self._any_query_params:
            if query_params:
                raise ValueError(
                    f"Both `any_query_params` and {list(query_params.keys())} were configured. Provide only one of none but not both."
                )
            query_params = ANY_QUERY_PARAMS

        return HttpRequest(
            url=f"https://api.stripe.com/v1/{self._resource}",
            query_params=query_params,
            headers={"Stripe-Account": self._account_id, "Authorization": f"Bearer {self._client_secret}"},
        )
