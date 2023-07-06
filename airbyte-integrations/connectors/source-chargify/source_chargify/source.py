#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class ChargifyStream(HttpStream, ABC):

    PER_PAGE = 200
    FIRST_PAGE = 1

    def __init__(self, *args, domain: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._domain = domain

    @property
    def url_base(self):
        return f"https://{self._domain}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        results = response.json()

        if results:
            if len(results) == self.PER_PAGE:
                url_query = urlparse(response.url).query
                query_params = parse_qs(url_query)

                new_params = {param_name: param_value[0] for param_name, param_value in query_params.items()}
                if "page" in new_params:
                    new_params["page"] = int(new_params["page"]) + 1
                return new_params

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        if next_page_token is None:
            return {"page": self.FIRST_PAGE, "per_page": self.PER_PAGE}

        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        yield response.json()


class Customers(ChargifyStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "customers.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgyNzY-list-or-find-customers
        # it returns a generator of Customers objects.
        customers = response.json()
        for customer in customers:
            yield customer["customer"]


class Subscriptions(ChargifyStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "subscriptions.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgzODk-list-subscriptions
        # it returns a generator of Subscriptions objects.
        subscriptions = response.json()
        for subscription in subscriptions:
            yield subscription["subscription"]


class Invoices(ChargifyStream):

    # Invoices use uid instead of id, see schemas for the invoice schema
    primary_key = "uid"

    def path(self, **kwargs) -> str:
        return "invoices.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/aa24a44561ce2-list-invoices
        invoices = response.json()["invoices"]
        for invoice in invoices:
            yield invoice


class Coupons(ChargifyStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "coupons.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/1c5e64abcf250-list-coupons
        coupons = response.json()
        for coupon in coupons:
            yield coupon["coupon"]


class Components(ChargifyStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "components.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/cb3576aacf9b4-list-components
        components = response.json()
        for component in components:
            yield component["component"]


class PaymentProfiles(ChargifyStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "payment_profiles.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/b752e67c19645-list-products
        payment_profiles = response.json()
        for payment_profile in payment_profiles:
            yield payment_profile["payment_profile"]


class Products(ChargifyStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "products.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/b3A6MTQxMDgzODk-list-subscriptions
        products = response.json()
        for product in products:
            yield product["product"]


class Transactions(ChargifyStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "transactions.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Chargify API: https://developers.chargify.com/docs/api-docs/21ec3a7e140c2-list-transactions
        transactions = response.json()
        for transaction in transactions:
            yield transaction["transaction"]


# Source
class SourceChargify(AbstractSource):
    BASIC_AUTH_PASSWORD = "x"

    def get_basic_auth(self, config: Mapping[str, Any]) -> requests.auth.HTTPBasicAuth:
        return requests.auth.HTTPBasicAuth(
            config["api_key"], SourceChargify.BASIC_AUTH_PASSWORD
        )  # https://developers.chargify.com/docs/api-docs/YXBpOjE0MTA4MjYx-chargify-api-documentation

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            authenticator = self.get_basic_auth(config)
            customers_gen = Customers(authenticator, domain=config["domain"]).read_records(SyncMode.full_refresh)
            next(customers_gen)
            subcriptions_gen = Subscriptions(authenticator, domain=config["domain"]).read_records(SyncMode.full_refresh)
            next(subcriptions_gen)
            invoices = Invoices(authenticator, domain=config["domain"]).read_records(SyncMode.full_refresh)
            next(invoices)
            coupons = Coupons(authenticator, domain=config["domain"]).read_records(SyncMode.full_refresh)
            next(coupons)

            return True, None
        except Exception as error:
            return False, f"Unable to connect to Chargify API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_basic_auth(config)
        return [
            Customers(authenticator, domain=config["domain"]),
            Subscriptions(authenticator, domain=config["domain"]),
            Invoices(authenticator, domain=config["domain"]),
            Coupons(authenticator, domain=config["domain"]),
            Components(authenticator, domain=config["domain"]),
            PaymentProfiles(authenticator, domain=config["domain"]),
            Products(authenticator, domain=config["domain"]),
            Transactions(authenticator, domain=config["domain"])
        ]
