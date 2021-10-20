#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Agents,
    Assets,
    Changes,
    Locations,
    Problems,
    Products,
    PurchaseOrders,
    Releases,
    Requesters,
    Software,
    Tickets,
    Vendors,
)


# Source
class HttpBasicAuthenticator(TokenAuthenticator):
    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic", **kwargs):
        auth_string = f"{auth[0]}:{auth[1]}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)


class SourceFreshservice(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = HttpBasicAuthenticator((config["api_key"], "")).get_auth_header()
        url = f'https://{config["domain_name"]}/api/v2/tickets'
        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = HttpBasicAuthenticator((config["api_key"], ""))
        return [
            Tickets(config),
            Problems(config),
            Changes(config),
            Releases(config),
            Requesters(config),
            Agents(config),
            Locations(config),
            Products(config),
            Vendors(config),
            Assets(config),
            PurchaseOrders(config),
            Software(config),
        ]
