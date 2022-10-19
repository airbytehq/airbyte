#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .api import Addresses, Charges, Collections, Customers, Discounts, Metafields, Onetimes, Orders, Products, Shop, Subscriptions


class RechargeTokenAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Recharge-Access-Token": self._token}


class SourceRecharge(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        auth = RechargeTokenAuthenticator(token=config["access_token"])
        stream = Shop(authenticator=auth)
        try:
            result = list(stream.read_records(SyncMode.full_refresh))[0]
            if stream.name in result.keys():
                return True, None
        except Exception as error:
            return False, f"Unable to connect to Recharge API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = RechargeTokenAuthenticator(token=config["access_token"])
        return [
            Addresses(authenticator=auth, start_date=config["start_date"]),
            Charges(authenticator=auth, start_date=config["start_date"]),
            Collections(authenticator=auth),
            Customers(authenticator=auth, start_date=config["start_date"]),
            Discounts(authenticator=auth, start_date=config["start_date"]),
            Metafields(authenticator=auth),
            Onetimes(authenticator=auth, start_date=config["start_date"]),
            Orders(authenticator=auth, start_date=config["start_date"]),
            Products(authenticator=auth),
            Shop(authenticator=auth),
            Subscriptions(authenticator=auth, start_date=config["start_date"]),
        ]
