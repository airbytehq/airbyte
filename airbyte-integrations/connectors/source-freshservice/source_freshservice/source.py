#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

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
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        kwargs = {
            "authenticator": HttpBasicAuthenticator((config["api_key"], "")),
            "start_date": config["start_date"],
            "domain_name": config["domain_name"],
        }
        try:
            tickets = Tickets(**kwargs).read_records(sync_mode=SyncMode.full_refresh)
            next(tickets)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        kwargs = {
            "authenticator": HttpBasicAuthenticator((config["api_key"], "")),
            "start_date": config["start_date"],
            "domain_name": config["domain_name"],
        }
        return [
            Tickets(**kwargs),
            Problems(**kwargs),
            Changes(**kwargs),
            Releases(**kwargs),
            Requesters(**kwargs),
            Agents(**kwargs),
            Locations(**kwargs),
            Products(**kwargs),
            Vendors(**kwargs),
            Assets(**kwargs),
            PurchaseOrders(**kwargs),
            Software(**kwargs),
        ]
