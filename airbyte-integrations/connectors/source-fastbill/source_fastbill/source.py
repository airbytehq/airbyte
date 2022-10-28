#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from requests.auth import HTTPBasicAuth
class FastbillStream(HttpStream, ABC):

    def __init__(self, *args, username: str = None, api_key: str = None,**kwargs):
        super().__init__(*args, **kwargs)
        self._username = username
        self._api_key = api_key

    API_OFFSET_LIMIT = 100

    @property
    def http_method(self) -> str:
        return "POST"
    url_base = " https://my.fastbill.com/api/1.0/api.php"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Content-type': 'application/json'}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        yield response.json()

class Invoices(FastbillStream):
    primary_key = "INVOICE_ID"

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        if next_page_token:
            return next_page_token
        else:
            return {
                "SERVICE": "invoice.get",
                "FILTER": {},
                "OFFSET": 0
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        def req_body(offset):
            return {
                "SERVICE": "invoice.get",
                "FILTER": {},
                "OFFSET": offset
            }

        response = response.json()
        offset = response["REQUEST"]["OFFSET"] if response["REQUEST"]["OFFSET"] >= 0 else None
        if offset is None:
            response_request = response["REQUEST"]["OFFSET"]
            raise Exception(f"No valid offset value found:{response_request}")

        if len(response["RESPONSE"]["INVOICES"]) == self.API_OFFSET_LIMIT:
            return req_body(offset + self.API_OFFSET_LIMIT)
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        invoices = response.json().get("RESPONSE", {}).get("INVOICES", [])
        yield from invoices
        # for invoice in invoices:
        #     yield self.schema_applier.apply_schema_transformations(
        #         invoice,
        #         self.get_json_schema()
        #     )


class RecurringInvoices(FastbillStream):
    primary_key = "INVOICE_ID"

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        if next_page_token:
            return next_page_token
        else:
            return {
                "SERVICE": "recurring.get",
                "FILTER": {},
                "OFFSET": 0
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        def req_body(offset):
            return {
                "SERVICE": "recurring.get",
                "FILTER": {},
                "OFFSET": offset
            }

        response = response.json()
        offset = response["REQUEST"]["OFFSET"] if response["REQUEST"]["OFFSET"] >= 0 else None
        if offset is None:
            response_request = response["REQUEST"]["OFFSET"]
            raise Exception(f"No valid offset value found:{response_request}")

        if len(response["RESPONSE"]["INVOICES"]) == self.API_OFFSET_LIMIT:
            return req_body(offset + self.API_OFFSET_LIMIT)
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        invoices = response.json().get("RESPONSE", {}).get("INVOICES", [])
        yield from invoices
        # for invoice in invoices:
        #     yield self.schema_applier.apply_schema_transformations(
        #         invoice,
        #         self.get_json_schema()
        #     )


class Products(FastbillStream):
    primary_key = "ARTICLE_ID"

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        if next_page_token:
            return next_page_token
        else:
            return {
                "SERVICE": "article.get",
                "FILTER": {},
                "OFFSET": 0
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        def req_body(offset):
            return {
                "SERVICE": "article.get",
                "FILTER": {},
                "OFFSET": offset
            }

        response = response.json()
        offset = response["REQUEST"]["OFFSET"] if response["REQUEST"]["OFFSET"] >= 0 else None
        if offset is None:
            response_request = response["REQUEST"]["OFFSET"]
            raise Exception(f"No valid offset value found:{response_request}")

        if len(response["RESPONSE"]["ARTICLES"]) == self.API_OFFSET_LIMIT:
            return req_body(offset + self.API_OFFSET_LIMIT)
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        products = response.json().get("RESPONSE", {}).get("ARTICLES", [])
        yield from products
        # for product in products:
        #     yield self.schema_applier.apply_schema_transformations(
        #         product,
        #         self.get_json_schema()
        #     )


class Revenues(FastbillStream):
    primary_key = "INVOICE_ID"

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        if next_page_token:
            return next_page_token
        else:
            return {
                "SERVICE": "revenue.get",
                "FILTER": {},
                "OFFSET": 0
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        def req_body(offset):
            return {
                "SERVICE": "revenue.get",
                "FILTER": {},
                "OFFSET": offset
            }

        response = response.json()
        offset = response["REQUEST"]["OFFSET"] if response["REQUEST"]["OFFSET"] >= 0 else None
        if offset is None:
            response_request = response["REQUEST"]["OFFSET"]
            raise Exception(f"No valid offset value found:{response_request}")

        if len(response["RESPONSE"]["REVENUES"]) == self.API_OFFSET_LIMIT:
            return req_body(offset + self.API_OFFSET_LIMIT)
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        customers = response.json().get("RESPONSE", {}).get("REVENUES", [])
        yield from customers
        # for customer in customers:
        #     yield self.schema_applier.apply_schema_transformations(
        #         customer,
        #         self.get_json_schema()
        #     )


class Customers(FastbillStream):
    primary_key = "CUSTOMER_ID"

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        if next_page_token:
            return next_page_token
        else:
            return {
                "SERVICE": "customer.get",
                "FILTER": {},
                "OFFSET": 0
            }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        def req_body(offset):
            return {
                "SERVICE": "customer.get",
                "FILTER": {},
                "OFFSET": offset
            }

        response = response.json()
        offset = response["REQUEST"]["OFFSET"] if response["REQUEST"]["OFFSET"] >= 0 else None
        if offset is None:
            response_request = response["REQUEST"]["OFFSET"]
            raise Exception(f"No valid offset value found:{response_request}")

        if len(response["RESPONSE"]["CUSTOMERS"]) == self.API_OFFSET_LIMIT:
            return req_body(offset + self.API_OFFSET_LIMIT)
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        customers = response.json().get("RESPONSE", {}).get("CUSTOMERS", [])
        yield from customers
        # for customer in customers:
        #     yield self.schema_applier.apply_schema_transformations(
        #         customer,
        #         self.get_json_schema()
        #     )


# Source
class SourceFastbill(AbstractSource):

    def get_basic_auth(self, config: Mapping[str, Any]) -> requests.auth.HTTPBasicAuth:
        return requests.auth.HTTPBasicAuth(
            config["username"], config["api_key"]
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = self.get_basic_auth(config)
            records = Customers(auth, **config).read_records(sync_mode=SyncMode.full_refresh)
            next(records, None)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Fastbill API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = self.get_basic_auth(config)
        return [
            Customers(auth, **config),
            Invoices(auth, **config),
            RecurringInvoices(auth, **config),
            Products(auth, **config),
            Revenues(auth, **config)
        ]
