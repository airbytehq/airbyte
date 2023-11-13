#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
        stream = Shop(config, authenticator=auth)
        try:
            result = list(stream.read_records(SyncMode.full_refresh))[0]
            if stream.name in result.keys():
                return True, None
        except Exception as error:
            return False, f"Unable to connect to Recharge API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = RechargeTokenAuthenticator(token=config["access_token"])
        return [
            Addresses(config, authenticator=auth),
            Charges(config, authenticator=auth),
            Collections(config, authenticator=auth),
            Customers(config, authenticator=auth),
            Discounts(config, authenticator=auth),
            Metafields(config, authenticator=auth),
            Onetimes(config, authenticator=auth),
            Orders(config, authenticator=auth),
            Products(config, authenticator=auth),
            Shop(config, authenticator=auth),
            Subscriptions(config, authenticator=auth),
        ]
