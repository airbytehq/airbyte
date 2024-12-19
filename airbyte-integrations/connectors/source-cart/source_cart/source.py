#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import codecs
import hashlib
import hmac
import urllib.parse
from enum import Enum
from functools import wraps
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from pendulum.parsing.exceptions import ParserError

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from .streams import Addresses, CustomersCart, OrderItems, OrderPayments, Orders, OrderStatuses, Products


class AuthMethod(Enum):
    CENTRAL_API_ROUTER = 1
    SINGLE_STORE_ACCESS_TOKEN = 2


class CustomHeaderAuthenticator(HttpAuthenticator):
    def __init__(self, access_token, store_name):
        self.auth_method = AuthMethod.SINGLE_STORE_ACCESS_TOKEN
        self._store_name = store_name
        self._access_token = access_token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-AC-Auth-Token": self._access_token}

    def url_base(self) -> str:
        return f"https://{self._store_name}/api/v1/"

    def extra_params(self, stream, params):
        return {}


class CentralAPIHeaderAuthenticator(HttpAuthenticator):
    def __init__(self, user_name, user_secret, site_id):
        self.auth_method = AuthMethod.CENTRAL_API_ROUTER
        self.user_name = user_name
        self.user_secret = user_secret
        self.site_id = site_id

    def get_auth_header(self) -> Mapping[str, Any]:
        """
        This method is not implemented here because for the Central API Router
        needs to build the header for each request based
        on path + parameters (next token, pagination, page size)
        To solve this the logic was moved to `request_headers` in CartStream class.
        """
        return {}

    def url_base(self) -> str:
        return "https://public.americommerce.com/api/v1/"

    def extra_params(self, stream, params):
        return self.generate_auth_signature(stream, params)

    def generate_auth_signature(self, stream, params) -> Mapping[str, Any]:
        """
        How to build signature:
        1. build a string concatenated with:
            request method (uppercase) & request path and query & provisioning user name
                example: GET&/api/v1/customers&myUser
        2. Generate HMACSHA256 hash using this string as the input, and the provisioning user secret as the key
        3. Base64 this hash to be used as the final value in the header
        """
        path_with_params = f"/api/v1/{stream.path()}?{urllib.parse.urlencode(params)}"
        msg = codecs.encode(f"GET&{path_with_params}&{self.user_name}")
        key = codecs.encode(self.user_secret)
        dig = hmac.new(key=key, msg=msg, digestmod=hashlib.sha256).digest()
        auth_signature = base64.b64encode(dig).decode()
        return {"X-AC-PUB-Site-ID": self.site_id, "X-AC-PUB-User": self.user_name, "X-AC-PUB-Auth-Signature": auth_signature}


class SourceCart(AbstractSource):
    def validate_config_values(func):
        """Check input config values for check_connection and stream functions. It will raise an exception if there is an parsing error"""

        @wraps(func)
        def decorator(self_, *args, **kwargs):
            for arg in args:
                if isinstance(arg, Mapping):
                    try:
                        # parse date strings by the pendulum library. It will raise the exception ParserError if it is some format mistakes.
                        pendulum.parse(arg["start_date"])
                        # try to check an end_date value. It can be ussed for different CI tests
                        end_date = arg.get("end_date")
                        if end_date:
                            pendulum.parse(end_date)
                    except ParserError as e:
                        raise Exception(f"{str(e)}. Example: 2021-01-01T00:00:00Z")
                    break

            return func(self_, *args, **kwargs)

        return decorator

    def get_auth(self, config):
        credentials = config.get("credentials", {})
        auth_method = credentials.get("auth_type")

        if auth_method == AuthMethod.CENTRAL_API_ROUTER.name:
            authenticator = CentralAPIHeaderAuthenticator(
                user_name=credentials["user_name"], user_secret=credentials["user_secret"], site_id=credentials["site_id"]
            )
        elif auth_method == AuthMethod.SINGLE_STORE_ACCESS_TOKEN.name:
            authenticator = CustomHeaderAuthenticator(access_token=credentials["access_token"], store_name=credentials["store_name"])
        else:
            raise NotImplementedError(f"Authentication method: {auth_method} not implemented.")

        return authenticator

    @validate_config_values
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = self.get_auth(config)
            stream = Products(authenticator=authenticator, start_date=config["start_date"])
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                return False, f"Please check your access token. Error: {repr(e)}"
            if isinstance(e, requests.exceptions.ConnectionError):
                err_message = f"Please check your `store_name` or internet connection. Error: {repr(e)}"
                return False, err_message
            return False, repr(e)

    @validate_config_values
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_auth(config)
        args = {
            "authenticator": authenticator,
            "start_date": config["start_date"],
            "end_date": config.get("end_date"),
        }
        return [
            CustomersCart(**args),
            Orders(**args),
            OrderPayments(**args),
            OrderStatuses(**args),
            OrderItems(**args),
            Products(**args),
            Addresses(**args),
        ]
