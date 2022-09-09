#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import codecs
import hashlib
import hmac
import urllib.parse
from datetime import datetime
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream

from .source import AuthMethod, CentralAPIHeaderAuthenticator, CustomHeaderAuthenticator


class CartStream(HttpStream, ABC):
    primary_key = "id"

    def __init__(
        self,
        start_date: str,
        end_date: str = None,
        authenticator: Union[CustomHeaderAuthenticator, CentralAPIHeaderAuthenticator] = None,
        **kwargs,
    ):
        self._start_date = start_date
        self._end_date = end_date
        self.authenticator = authenticator
        super().__init__(**kwargs)

    @property
    def url_base(self) -> str:
        if self.authenticator.auth_method == AuthMethod.CENTRAL_API_ROUTER:
            return "https://public.americommerce.com/api/v1/"
        else:
            return f"https://{self.authenticator.store_name}/api/v1/"

    @property
    def data_field(self) -> str:
        """
        Field of the response containing data.
        By default the value self.name will be used if this property is empty or None
        """
        return None

    def path(self, **kwargs) -> str:
        return self.name

    @property
    def max_retries(self) -> Union[int, None]:
        return 3

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        We dont need to check the response.status_code == 429 since this header exists only in this case.
        Some endpoints or sometimes Cart.com API returns a datetie instead of the float value to wait to next request.
        Also after calculating the float when Cart.com return a datetime using the value directly
        causes Server Error after a few attempts. Because of this was created the `server_backoff` variable to give time
        to server recover from too many requests. 
        """
        server_backoff = 3
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            self.logger.info(f"Backoff for stream name: {self.__class__.__name__}")
            self.logger.info(response.status_code)
            self.logger.info(response.headers)
            try:
                return float(retry_after)
            except ValueError:
                retry_after_datetime = datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S %Z")
                return float(server_backoff * abs(retry_after_datetime - datetime.now()).seconds)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()

        if response_json.get("next_page"):
            next_query_string = urllib.parse.urlsplit(response_json.get("next_page")).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        auth_signature = {}
        if self.authenticator.auth_method == AuthMethod.CENTRAL_API_ROUTER:
            params = self.request_params(self, **kwargs)
            auth_signature = self.generate_auth_signature(self, params)
        return dict({"Cache-Control": "no-cache", "Content-Type": "application/json"}, **auth_signature)

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        result = response_json.get(self.data_field or self.name, [])
        yield from result

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"count": 1000}
        if next_page_token:
            params.update(next_page_token)
        return params

    def generate_auth_signature(self, params) -> Mapping[str, Any]:
        """
        How to build signature:
        1. build a string concatenated with:
            request method (uppercase) & request path and query & provisioning user name
                example: GET&/api/v1/customers&myUser
        2. Generate HMACSHA256 hash using this string as the input, and the provisioning user secret as the key
        3. Base64 this hash to be used as the final value in the header
        """
        path_with_params = f"{self.path()}&{urllib.parse.encode(params)}"
        msg = codecs.encode(f"GET&{path_with_params}&{self.authenticator.user_name}")
        key = codecs.encode(self.authenticator.user_secret)
        dig = hmac.new(key=key, msg=msg, digestmod=hashlib.sha256).digest()
        auth_signature = base64.b64encode(dig).decode()
        return {"X-AC-PUB-Site-ID": self._site_id, "X-AC-PUB-User": self._user_name, "X-AC-PUB-Auth-Signature": auth_signature}


class IncrementalCartStream(CartStream, ABC):

    state_checkpoint_interval = 1000
    cursor_field = "updated_at"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        Generates a query for incremental logic

        Docs: https://developers.cart.com/docs/rest-api/docs/query_syntax.md
        """
        params = super().request_params(stream_state=stream_state, **kwargs)
        cursor_value = stream_state.get(self.cursor_field) or self._start_date
        params["sort"] = self.cursor_field
        start_date = max(cursor_value, self._start_date)
        query = f"gt:{start_date}"
        if self._end_date and self._end_date > start_date:
            query += f" AND lt:{self._end_date}"

        params[self.cursor_field] = query
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        if current_state:
            return {self.cursor_field: max(latest_state, current_state)}
        return {}


class CustomersCart(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1customers/get
    """

    data_field = "customers"

    def path(self, **kwargs) -> str:
        return self.data_field


class Orders(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1orders/get
    """


class OrderPayments(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_payments/get
    """

    data_field = "payments"


class OrderItems(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_items/get
    """

    data_field = "items"


class OrderStatuses(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/ff5ada86bc8a0-get-order-statuses
    """

    data_field = "order_statuses"


class Products(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/restapi.json/paths/~1products/get
    """


class Addresses(IncrementalCartStream):
    """
    Docs: https://developers.cart.com/docs/rest-api/b3A6MjMzMTc3Njc-get-addresses
    """
