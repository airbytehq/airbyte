#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from functools import wraps
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from pendulum.parsing.exceptions import ParserError

from .streams import Addresses, CustomersCart, OrderItems, OrderPayments, Orders, Products


class CustomHeaderAuthenticator(HttpAuthenticator):
    def __init__(self, access_token):
        self._access_token = access_token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-AC-Auth-Token": self._access_token}


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

    @validate_config_values
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = CustomHeaderAuthenticator(access_token=config["access_token"])

            stream = Products(authenticator=authenticator, start_date=config["start_date"], store_name=config["store_name"])
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
        authenticator = CustomHeaderAuthenticator(access_token=config["access_token"])
        args = {
            "authenticator": authenticator,
            "start_date": config["start_date"],
            "store_name": config["store_name"],
            "end_date": config.get("end_date"),
        }
        return [CustomersCart(**args), Orders(**args), OrderPayments(**args), OrderItems(**args), Products(**args), Addresses(**args)]
