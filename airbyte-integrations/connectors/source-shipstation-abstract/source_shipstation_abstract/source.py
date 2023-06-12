#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
import base64

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from requests.auth import AuthBase
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    ShipstationAbstractStream,
    Users, 
    Carriers,
    MarketPlaces,
    Stores,
    Shipments,
    Fulfillments,
    Customers,
    Products
    )


class BasicAuthenticator(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Basic {self.token}"
        return r


class SourceShipstationAbstract(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            api_key = config.get("api_key")
            api_secret = config.get("api_secret")
            url = Users().path()
            payload = {}
            response=requests.get(url, auth=(api_key,api_secret), params=payload,)
            json_response = response.json()
            contains_user_id = any('userId' in item for item in json_response)
            if contains_user_id:
                return True, None
            return False, "Unable to fetch data from Shipstation API"
        except Exception as error:
            return False, f"Unable to connect to Shipstation API with the provided credentials - {error}"
        



    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        api_key = config.get("api_key")
        api_secret = config.get("api_secret")
        auth_token = f"{api_key}:{api_secret}"
        base64_auth_token = base64.b64encode(auth_token.encode("utf-8")).decode("utf-8")

        auth = BasicAuthenticator(base64_auth_token)
        return [Carriers(authenticator=auth),
                Users(authenticator=auth),
                MarketPlaces(authenticator=auth), 
                Shipments(authenticator=auth),
                Fulfillments(authenticator=auth),
                Customers(authenticator=auth),
                Products(authenticator=auth),
                Stores(authenticator=auth),
                ]