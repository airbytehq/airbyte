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
from source_fastbill.helpers import get_next_page_token, get_request_body_json


class FastbillStream(HttpStream, ABC):
    url_base = " https://my.fastbill.com/api/1.0/api.php"
    API_OFFSET_LIMIT = 100

    def __init__(self, *args, username: str = None, api_key: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        # self.endpoint = None
        self._username = username
        self._api_key = api_key
        # self.data = None

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-type": "application/json"}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        return get_request_body_json(next_page_token, endpoint=self.endpoint)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return get_next_page_token(
            response=response, response_key=self.data, API_OFFSET_LIMIT=self.API_OFFSET_LIMIT, endpoint=self.endpoint
        )

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("RESPONSE", {}).get(self.data, [])


class Invoices(FastbillStream):
    primary_key = "INVOICE_ID"
    data = "INVOICES"
    endpoint = "invoice"


class RecurringInvoices(FastbillStream):
    primary_key = "INVOICE_ID"
    data = "INVOICES"
    endpoint = "recurring"


class Products(FastbillStream):
    primary_key = "ARTICLE_ID"
    data = "ARTICLES"
    endpoint = "article"


class Revenues(FastbillStream):
    primary_key = "INVOICE_ID"
    data = "REVENUES"
    endpoint = "revenue"


class Customers(FastbillStream):
    primary_key = "CUSTOMER_ID"
    data = "CUSTOMERS"
    endpoint = "customer"


# Source
class SourceFastbill(AbstractSource):
    def get_basic_auth(self, config: Mapping[str, Any]) -> requests.auth.HTTPBasicAuth:
        return requests.auth.HTTPBasicAuth(config["username"], config["api_key"])

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
            Revenues(auth, **config),
        ]
